"""Persistência append-only dos payloads e metadados de extração."""

from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any
from uuid import uuid4

from pydantic import BaseModel

from f1.pipeline.common import (
    ENDPOINTS,
    EndpointDefinition,
    IngestionResult,
)
from f1.pipeline.common import (
    canonical_json as _canonical_json,
)
from f1.pipeline.common import (
    canonical_json_hash as _canonical_json_hash,
)
from f1.pipeline.common import (
    duckdb_type as _duckdb_type,
)
from f1.pipeline.common import (
    sql_identifier as _sql_identifier,
)
from f1.pipeline.database import DatabaseLayer


class RawLayer(DatabaseLayer):
    """Grava as respostas da API sem sobrescrever versões anteriores."""

    @staticmethod
    def _endpoint(endpoint: str) -> tuple[str, EndpointDefinition]:
        normalized = endpoint.strip("/").split("/")[-1]
        try:
            return normalized, ENDPOINTS[normalized]
        except KeyError as exc:
            raise ValueError(f"Endpoint OpenF1 não suportado: {endpoint}") from exc

    @staticmethod
    def _payload(record: BaseModel | Mapping[str, Any]) -> dict[str, Any]:
        if isinstance(record, BaseModel):
            return record.model_dump(mode="json")
        if isinstance(record, Mapping):
            return dict(record)
        raise TypeError("Cada registro deve ser um modelo Pydantic ou um mapeamento.")

    @staticmethod
    def _raw_value(value: Any, column_type: str) -> Any:
        if value is None:
            return None
        if column_type == "JSON":
            return _canonical_json(value)
        if column_type == "TIMESTAMPTZ" and isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=UTC)
            return value.astimezone(UTC)
        if column_type == "BOOLEAN":
            return value if isinstance(value, bool) else None
        if column_type in {"BIGINT", "INTEGER"}:
            return (
                value
                if isinstance(value, int) and not isinstance(value, bool)
                else None
            )
        if column_type == "DOUBLE":
            return (
                float(value)
                if isinstance(value, (float, int)) and not isinstance(value, bool)
                else None
            )
        return value if isinstance(value, str) else None

    def _create_raw_table(
        self, definition: EndpointDefinition
    ) -> list[tuple[str, str]]:
        model_fields = definition.model.model_fields
        field_types = [
            (name, _duckdb_type(field.annotation))
            for name, field in model_fields.items()
        ]
        context_fields = [
            (name, "JSON")
            for name in ("meeting_key", "session_key")
            if name not in model_fields
        ]
        columns = [
            ("id_registro_raw", "VARCHAR"),
            ("id_ingestao", "VARCHAR"),
            ("data_extracao", "TIMESTAMPTZ"),
            ("endpoint_origem", "VARCHAR"),
            ("ano_referencia", "INTEGER"),
            ("hash_conteudo", "VARCHAR"),
            ("payload_original", "JSON"),
            *field_types,
            *context_fields,
        ]
        declarations = [
            f"{_sql_identifier(name)} {column_type}" for name, column_type in columns
        ]
        declarations[0] += " PRIMARY KEY"
        table_name = _sql_identifier(definition.raw_table)
        self._db().execute(
            f"CREATE TABLE IF NOT EXISTS raw.{table_name} ({', '.join(declarations)})"
        )
        return columns

    def ingest_raw(
        self,
        endpoint: str,
        records: Iterable[BaseModel | Mapping[str, Any]],
        *,
        year_reference: int | None = None,
        meeting_key: int | str | None = None,
        session_key: int | str | None = None,
    ) -> IngestionResult:
        """Grava uma extração RAW e registra o status de execução e sessão."""
        if self._connection is None:
            self.initialize()
        endpoint_name, definition = self._endpoint(endpoint)
        payloads = [self._payload(record) for record in records]
        started_at = datetime.now(UTC)
        execution_id = str(uuid4())
        extraction_id = str(uuid4())
        self._start_execution(execution_id, "INGESTAO", started_at)

        if not payloads:
            finished_at = datetime.now(UTC)
            self._db().execute(
                """
                INSERT INTO metadata.historico_extracoes (
                    id_extracao, id_execucao, endpoint, meeting_key, session_key,
                    data_inicio, data_fim, status, quantidade_registros
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'SEM_DADOS', 0)
                """,
                [
                    extraction_id,
                    execution_id,
                    endpoint_name,
                    str(meeting_key) if meeting_key is not None else None,
                    str(session_key) if session_key is not None else None,
                    started_at,
                    finished_at,
                ],
            )
            self._record_session_status(
                session_key,
                meeting_key,
                year_reference,
                finished_at,
                None,
                "SEM_DADOS",
            )
            self._finish_execution(execution_id, "SEM_DADOS", finished_at, 1, 0)
            return IngestionResult(execution_id, extraction_id, "SEM_DADOS", 0, None)

        raw_columns = self._create_raw_table(definition)
        record_hashes = [_canonical_json_hash(payload) for payload in payloads]
        batch_hash = sha256("".join(sorted(record_hashes)).encode("utf-8")).hexdigest()
        insert_columns = ", ".join(_sql_identifier(name) for name, _ in raw_columns)
        insert_values = ", ".join(
            "CAST(? AS JSON)" if column_type == "JSON" else "?"
            for _, column_type in raw_columns
        )
        table_name = _sql_identifier(definition.raw_table)

        try:
            self._db().execute("BEGIN TRANSACTION")
            for payload, record_hash in zip(payloads, record_hashes, strict=True):
                record_year = year_reference or payload.get("year")
                record_meeting = payload.get("meeting_key", meeting_key)
                record_session = payload.get("session_key", session_key)
                values: dict[str, Any] = {
                    "id_registro_raw": str(uuid4()),
                    "id_ingestao": execution_id,
                    "data_extracao": started_at,
                    "endpoint_origem": endpoint_name,
                    "ano_referencia": record_year,
                    "hash_conteudo": record_hash,
                    "payload_original": payload,
                    **payload,
                }
                if "meeting_key" not in payload:
                    values["meeting_key"] = record_meeting
                if "session_key" not in payload:
                    values["session_key"] = record_session
                row_values = [
                    self._raw_value(values.get(name), column_type)
                    for name, column_type in raw_columns
                ]
                self._db().execute(
                    f"INSERT INTO raw.{table_name} ({insert_columns}) "
                    f"VALUES ({insert_values})",
                    row_values,
                )
            finished_at = datetime.now(UTC)
            self._db().execute(
                """
                INSERT INTO metadata.historico_extracoes (
                    id_extracao, id_execucao, endpoint, meeting_key, session_key,
                    data_inicio, data_fim, status, quantidade_registros, hash_conteudo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'CONCLUIDA', ?, ?)
                """,
                [
                    extraction_id,
                    execution_id,
                    endpoint_name,
                    str(meeting_key) if meeting_key is not None else None,
                    str(session_key) if session_key is not None else None,
                    started_at,
                    finished_at,
                    len(payloads),
                    batch_hash,
                ],
            )
            for payload in payloads:
                self._record_session_status(
                    payload.get("session_key", session_key),
                    payload.get("meeting_key", meeting_key),
                    year_reference or payload.get("year"),
                    finished_at,
                    batch_hash,
                    "CONCLUIDA",
                )
            self._finish_execution(
                execution_id, "CONCLUIDA", finished_at, 1, len(payloads)
            )
            self._db().execute("COMMIT")
        except Exception as exc:
            self._db().execute("ROLLBACK")
            finished_at = datetime.now(UTC)
            self._db().execute(
                """
                INSERT INTO metadata.historico_extracoes (
                    id_extracao, id_execucao, endpoint, meeting_key, session_key,
                    data_inicio, data_fim, status, mensagem_erro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'FALHA', ?)
                """,
                [
                    extraction_id,
                    execution_id,
                    endpoint_name,
                    str(meeting_key) if meeting_key is not None else None,
                    str(session_key) if session_key is not None else None,
                    started_at,
                    finished_at,
                    str(exc),
                ],
            )
            self._finish_execution(execution_id, "FALHA", finished_at, 1, 0, str(exc))
            raise

        return IngestionResult(
            execution_id,
            extraction_id,
            "CONCLUIDA",
            len(payloads),
            batch_hash,
        )
