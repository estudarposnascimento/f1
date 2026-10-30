"""Validação e modelagem dimensional/factual da camada REFINED."""

import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import ValidationError

from f1.core.models import OpenF1BaseModel
from f1.pipeline.common import (
    ENDPOINTS,
    TransformationResult,
)
from f1.pipeline.common import (
    canonical_json as _canonical_json,
)
from f1.pipeline.common import (
    canonical_json_hash as _canonical_json_hash,
)
from f1.pipeline.common import (
    refined_type as _refined_type,
)
from f1.pipeline.common import (
    sql_identifier as _sql_identifier,
)
from f1.pipeline.raw import RawLayer
from f1.utils.datetime import parse_iso_datetime


class RefinedLayer(RawLayer):
    """Cria e popula as estruturas normalizadas e relacionáveis."""

    def _create_generic_refined_table(
        self, table: str, model: type[OpenF1BaseModel]
    ) -> list[tuple[str, str]]:
        fields = [
            (name, _refined_type(name, field.annotation))
            for name, field in model.model_fields.items()
        ]
        columns = [
            ("id_registro_raw", "VARCHAR"),
            ("id_execucao", "VARCHAR"),
            ("id_ingestao", "VARCHAR"),
            ("data_extracao", "TIMESTAMPTZ"),
            ("data_processamento", "TIMESTAMPTZ"),
            ("hash_conteudo", "VARCHAR"),
            *fields,
        ]
        declarations = [
            f"{_sql_identifier(name)} {column_type}" for name, column_type in columns
        ]
        declarations[0] += " PRIMARY KEY"
        declarations[5] += " UNIQUE"
        self._db().execute(
            f"CREATE TABLE IF NOT EXISTS refined.{_sql_identifier(table)} "
            f"({', '.join(declarations)})"
        )
        return columns

    @staticmethod
    def _refined_value(name: str, value: Any, column_type: str) -> Any:
        if value is None:
            return None
        if column_type == "TIMESTAMPTZ":
            return parse_iso_datetime(value)
        if column_type == "JSON":
            return _canonical_json(value)
        if column_type == "VARCHAR":
            return str(value) if name in {"meeting_key", "session_key"} else value
        return RefinedLayer._raw_value(value, column_type)

    def _insert_refined_record(
        self,
        table: str,
        model: type[OpenF1BaseModel],
        values: dict[str, Any],
        raw_record_id: str,
        ingestion_id: str,
        execution_id: str,
        extracted_at: datetime,
        content_hash: str,
    ) -> None:
        columns = self._create_generic_refined_table(table, model)
        insert_columns = ", ".join(_sql_identifier(name) for name, _ in columns)
        insert_values = ", ".join(
            "CAST(? AS JSON)" if column_type == "JSON" else "?"
            for _, column_type in columns
        )
        row_values = [
            raw_record_id,
            execution_id,
            ingestion_id,
            extracted_at,
            datetime.now(UTC),
            content_hash,
        ]
        row_values.extend(
            self._refined_value(name, values.get(name), column_type)
            for name, column_type in columns[6:]
        )
        self._db().execute(
            f"INSERT INTO refined.{_sql_identifier(table)} "
            f"({insert_columns}) VALUES ({insert_values}) ON CONFLICT DO NOTHING",
            row_values,
        )

    def _create_scd2_tables(self) -> None:
        self._db().execute(
            """
            CREATE TABLE IF NOT EXISTS refined.dim_pilotos (
                id_piloto VARCHAR PRIMARY KEY,
                natural_key VARCHAR NOT NULL,
                driver_number BIGINT NOT NULL,
                full_name VARCHAR NOT NULL,
                name_acronym VARCHAR NOT NULL,
                team_name VARCHAR,
                team_colour VARCHAR,
                meeting_key VARCHAR,
                session_key VARCHAR,
                ano_referencia INTEGER,
                valido_desde TIMESTAMPTZ NOT NULL,
                valido_ate TIMESTAMPTZ,
                versao_atual BOOLEAN NOT NULL,
                hash_conteudo VARCHAR NOT NULL,
                id_registro_raw VARCHAR NOT NULL,
                id_ingestao VARCHAR NOT NULL,
                id_execucao VARCHAR NOT NULL,
                UNIQUE (natural_key, hash_conteudo)
            )
            """
        )
        self._db().execute(
            """
            CREATE TABLE IF NOT EXISTS refined.dim_equipes (
                id_equipe VARCHAR PRIMARY KEY,
                natural_key VARCHAR NOT NULL,
                team_name VARCHAR NOT NULL,
                team_colour VARCHAR,
                ano_referencia INTEGER,
                valido_desde TIMESTAMPTZ NOT NULL,
                valido_ate TIMESTAMPTZ,
                versao_atual BOOLEAN NOT NULL,
                hash_conteudo VARCHAR NOT NULL,
                id_registro_raw VARCHAR NOT NULL,
                id_ingestao VARCHAR NOT NULL,
                id_execucao VARCHAR NOT NULL,
                UNIQUE (natural_key, hash_conteudo)
            )
            """
        )

    def _infer_year(
        self, payload: dict[str, Any], year_reference: int | None
    ) -> int | None:
        if year_reference is not None:
            return year_reference
        if payload.get("year") is not None:
            return int(payload["year"])
        meeting_key = payload.get("meeting_key")
        if meeting_key is None:
            return None
        exists = (
            self._db()
            .execute(
                """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'raw' AND table_name = 'grandes_premios'
            """
            )
            .fetchone()
        )
        if exists is None:
            return None
        year_row = (
            self._db()
            .execute(
                """
            SELECT TRY_CAST(json_extract_string(payload_original, '$.year') AS INTEGER)
            FROM raw.grandes_premios
            WHERE json_extract_string(payload_original, '$.meeting_key') = ?
            LIMIT 1
            """,
                [str(meeting_key)],
            )
            .fetchone()
        )
        return year_row[0] if year_row else None

    def _insert_scd2_record(
        self,
        table: str,
        payload: dict[str, Any],
        raw_record_id: str,
        ingestion_id: str,
        execution_id: str,
        extracted_at: datetime,
        year_reference: int | None,
    ) -> None:
        self._create_scd2_tables()
        year = self._infer_year(payload, year_reference)
        context = (
            f"season:{year}"
            if year is not None
            else f"meeting:{payload.get('meeting_key')}"
        )

        if table == "dim_pilotos":
            natural_key = f"{payload['driver_number']}|{context}"
            tracked = {
                name: payload.get(name)
                for name in (
                    "driver_number",
                    "full_name",
                    "name_acronym",
                    "team_name",
                    "team_colour",
                )
            }
            version_hash = _canonical_json_hash(tracked)
            current = (
                self._db()
                .execute(
                    "SELECT hash_conteudo FROM refined.dim_pilotos "
                    "WHERE natural_key = ? AND versao_atual",
                    [natural_key],
                )
                .fetchone()
            )
            if current and current[0] == version_hash:
                return
            previous_version = (
                self._db()
                .execute(
                    "SELECT 1 FROM refined.dim_pilotos "
                    "WHERE natural_key = ? AND hash_conteudo = ?",
                    [natural_key, version_hash],
                )
                .fetchone()
            )
            if previous_version:
                return
            self._db().execute(
                "UPDATE refined.dim_pilotos SET valido_ate = ?, versao_atual = FALSE "
                "WHERE natural_key = ? AND versao_atual",
                [extracted_at, natural_key],
            )
            self._db().execute(
                """
                INSERT INTO refined.dim_pilotos VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, TRUE, ?, ?, ?, ?
                )
                """,
                [
                    str(uuid4()),
                    natural_key,
                    payload["driver_number"],
                    payload["full_name"],
                    payload["name_acronym"],
                    payload.get("team_name"),
                    payload.get("team_colour"),
                    str(payload.get("meeting_key"))
                    if payload.get("meeting_key") is not None
                    else None,
                    str(payload.get("session_key"))
                    if payload.get("session_key") is not None
                    else None,
                    year,
                    extracted_at,
                    version_hash,
                    raw_record_id,
                    ingestion_id,
                    execution_id,
                ],
            )
            return

        team_name = payload.get("team_name")
        if not team_name:
            return
        natural_key = f"{team_name.casefold()}|{context}"
        tracked = {"team_name": team_name, "team_colour": payload.get("team_colour")}
        version_hash = _canonical_json_hash(tracked)
        current = (
            self._db()
            .execute(
                "SELECT hash_conteudo FROM refined.dim_equipes "
                "WHERE natural_key = ? AND versao_atual",
                [natural_key],
            )
            .fetchone()
        )
        if current and current[0] == version_hash:
            return
        previous_version = (
            self._db()
            .execute(
                "SELECT 1 FROM refined.dim_equipes "
                "WHERE natural_key = ? AND hash_conteudo = ?",
                [natural_key, version_hash],
            )
            .fetchone()
        )
        if previous_version:
            return
        self._db().execute(
            "UPDATE refined.dim_equipes SET valido_ate = ?, versao_atual = FALSE "
            "WHERE natural_key = ? AND versao_atual",
            [extracted_at, natural_key],
        )
        self._db().execute(
            """
            INSERT INTO refined.dim_equipes VALUES (
                ?, ?, ?, ?, ?, ?, NULL, TRUE, ?, ?, ?, ?
            )
            """,
            [
                str(uuid4()),
                natural_key,
                team_name,
                payload.get("team_colour"),
                year,
                extracted_at,
                version_hash,
                raw_record_id,
                ingestion_id,
                execution_id,
            ],
        )

    def _insert_circuit(
        self,
        payload: dict[str, Any],
        raw_record_id: str,
        ingestion_id: str,
        execution_id: str,
        extracted_at: datetime,
        content_hash: str,
    ) -> None:
        self._db().execute(
            """
            CREATE TABLE IF NOT EXISTS refined.dim_circuitos (
                circuit_key BIGINT PRIMARY KEY,
                circuit_short_name VARCHAR NOT NULL,
                circuit_type VARCHAR,
                location VARCHAR,
                country_name VARCHAR,
                country_code VARCHAR,
                id_registro_raw VARCHAR NOT NULL,
                id_ingestao VARCHAR NOT NULL,
                id_execucao VARCHAR NOT NULL,
                data_extracao TIMESTAMPTZ NOT NULL,
                data_processamento TIMESTAMPTZ NOT NULL,
                hash_conteudo VARCHAR NOT NULL
            )
            """
        )
        self._db().execute(
            """
            INSERT INTO refined.dim_circuitos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (circuit_key) DO UPDATE SET
                circuit_short_name = excluded.circuit_short_name,
                circuit_type = excluded.circuit_type,
                location = excluded.location,
                country_name = excluded.country_name,
                country_code = excluded.country_code,
                id_registro_raw = excluded.id_registro_raw,
                id_ingestao = excluded.id_ingestao,
                id_execucao = excluded.id_execucao,
                data_extracao = excluded.data_extracao,
                data_processamento = excluded.data_processamento,
                hash_conteudo = excluded.hash_conteudo
            """,
            [
                payload["circuit_key"],
                payload["circuit_short_name"],
                payload.get("circuit_type"),
                payload.get("location"),
                payload.get("country_name"),
                payload.get("country_code"),
                raw_record_id,
                ingestion_id,
                execution_id,
                extracted_at,
                datetime.now(UTC),
                content_hash,
            ],
        )

    def _record_rejection(
        self,
        execution_id: str,
        endpoint: str,
        raw_table: str,
        session_key: Any,
        payload: dict[str, Any],
        error: Exception,
    ) -> None:
        field_name: str | None = None
        rejected_value: Any = None
        reason = str(error)
        if isinstance(error, ValidationError):
            details = error.errors(include_url=False)
            if details:
                field_name = ".".join(str(item) for item in details[0]["loc"])
                rejected_value = details[0].get("input")
                reason = details[0]["msg"]
        self._db().execute(
            """
            INSERT INTO refined.rejeicoes VALUES (
                ?, ?, ?, ?, ?, CAST(? AS JSON), ?, CAST(? AS JSON), ?, ?
            )
            """,
            [
                str(uuid4()),
                execution_id,
                endpoint,
                raw_table,
                str(session_key) if session_key is not None else None,
                _canonical_json(payload),
                field_name,
                _canonical_json(rejected_value) if rejected_value is not None else None,
                reason,
                datetime.now(UTC),
            ],
        )

    def _validate_foreign_keys(
        self,
        endpoint: str,
        payload: dict[str, Any],
        year_reference: int | None,
    ) -> None:
        if endpoint == "meetings":
            return

        meeting_key = payload.get("meeting_key")
        session_key = payload.get("session_key")
        if endpoint == "sessions":
            if not self._refined_table_exists("dim_grandes_premios"):
                raise ValueError("Dimensão de Grandes Prêmios ainda não foi carregada.")
            parent = (
                self._db()
                .execute(
                    "SELECT 1 FROM refined.dim_grandes_premios WHERE meeting_key = ? LIMIT 1",
                    [str(meeting_key)],
                )
                .fetchone()
            )
            if parent is None:
                raise ValueError(
                    f"Grande Prêmio {meeting_key} não encontrado em REFINED."
                )
            return

        if not self._refined_table_exists("dim_sessoes"):
            raise ValueError("Dimensão de sessões ainda não foi carregada.")
        session = (
            self._db()
            .execute(
                """
            SELECT meeting_key FROM refined.dim_sessoes
            WHERE session_key = ?
            ORDER BY data_processamento DESC
            LIMIT 1
            """,
                [str(session_key)],
            )
            .fetchone()
        )
        if session is None:
            raise ValueError(f"Sessão {session_key} não encontrada em REFINED.")
        if meeting_key is not None and session[0] != str(meeting_key):
            raise ValueError(
                f"Sessão {session_key} não pertence ao Grande Prêmio {meeting_key}."
            )

        if endpoint == "overtakes":
            driver_numbers = [
                payload.get("overtaking_driver_number"),
                payload.get("overtaken_driver_number"),
            ]
        elif endpoint == "drivers":
            driver_numbers = []
        else:
            driver_numbers = [payload.get("driver_number")]

        for driver_number in (
            number for number in driver_numbers if number is not None
        ):
            if not self._refined_table_exists("dim_pilotos"):
                driver = None
            elif year_reference is not None:
                driver = (
                    self._db()
                    .execute(
                        """
                    SELECT 1 FROM refined.dim_pilotos
                    WHERE driver_number = ? AND ano_referencia = ?
                    LIMIT 1
                    """,
                        [driver_number, year_reference],
                    )
                    .fetchone()
                )
            else:
                driver = (
                    self._db()
                    .execute(
                        """
                    SELECT 1 FROM refined.dim_pilotos
                    WHERE driver_number = ? AND meeting_key = ?
                    LIMIT 1
                    """,
                        [driver_number, str(meeting_key)],
                    )
                    .fetchone()
                )
            if driver is None:
                raise ValueError(
                    f"Piloto {driver_number} não encontrado no contexto da sessão."
                )

        if endpoint == "championship_teams":
            team = None
            if self._refined_table_exists("dim_equipes"):
                team = (
                    self._db()
                    .execute(
                        "SELECT 1 FROM refined.dim_equipes WHERE team_name = ? LIMIT 1",
                        [payload["team_name"]],
                    )
                    .fetchone()
                )
            if team is None:
                raise ValueError(
                    f"Equipe {payload['team_name']} não encontrada em REFINED."
                )

    def _set_session_processing_status(self, session_key: Any, status: str) -> None:
        if session_key is None:
            return
        self._db().execute(
            """
            UPDATE metadata.controle_sessoes
            SET status_processamento = ?, data_ultima_alteracao = ?
            WHERE session_key = ?
            """,
            [status, datetime.now(UTC), str(session_key)],
        )

    def _transform_endpoint(self, endpoint: str) -> TransformationResult:
        endpoint_name, definition = self._endpoint(endpoint)
        execution_id = str(uuid4())
        started_at = datetime.now(UTC)
        self._start_execution(execution_id, "REFINED", started_at)
        table_exists = (
            self._db()
            .execute(
                """
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'raw' AND table_name = ?
            """,
                [definition.raw_table],
            )
            .fetchone()
        )
        if table_exists is None:
            self._finish_execution(execution_id, "SEM_DADOS", datetime.now(UTC), 1, 0)
            return TransformationResult(execution_id, endpoint_name, "SEM_DADOS", 0, 0)

        raw_rows = (
            self._db()
            .execute(
                f"""
            SELECT id_registro_raw, id_ingestao, CAST(data_extracao AS VARCHAR),
                   ano_referencia, hash_conteudo, payload_original
            FROM raw.{_sql_identifier(definition.raw_table)}
            ORDER BY data_extracao, id_registro_raw
            """
            )
            .fetchall()
        )
        if not raw_rows:
            self._finish_execution(execution_id, "SEM_DADOS", datetime.now(UTC), 1, 0)
            return TransformationResult(execution_id, endpoint_name, "SEM_DADOS", 0, 0)

        processed = 0
        rejected = 0
        session_statuses: dict[str, bool] = {}
        self._db().execute("BEGIN TRANSACTION")
        try:
            for raw_row in raw_rows:
                (
                    raw_id,
                    ingestion_id,
                    extracted_at,
                    year_reference,
                    content_hash,
                    raw_json,
                ) = raw_row
                extracted_at = parse_iso_datetime(extracted_at)
                payload = (
                    json.loads(raw_json) if isinstance(raw_json, str) else raw_json
                )
                session = payload.get("session_key")
                try:
                    model = definition.model.model_validate(payload)
                    normalized = model.model_dump(mode="python")
                    self._validate_foreign_keys(
                        endpoint_name, normalized, year_reference
                    )
                    for target in definition.refined_tables:
                        if target in {"dim_pilotos", "dim_equipes"}:
                            self._insert_scd2_record(
                                target,
                                normalized,
                                raw_id,
                                ingestion_id,
                                execution_id,
                                extracted_at,
                                year_reference,
                            )
                        elif target == "dim_circuitos":
                            self._insert_circuit(
                                normalized,
                                raw_id,
                                ingestion_id,
                                execution_id,
                                extracted_at,
                                content_hash,
                            )
                        else:
                            self._insert_refined_record(
                                target,
                                definition.model,
                                normalized,
                                raw_id,
                                ingestion_id,
                                execution_id,
                                extracted_at,
                                content_hash,
                            )
                    processed += 1
                    if session is not None:
                        session_statuses[str(session)] = True
                except (ValidationError, TypeError, ValueError) as exc:
                    self._record_rejection(
                        execution_id,
                        endpoint_name,
                        definition.raw_table,
                        session,
                        payload,
                        exc,
                    )
                    rejected += 1
                    if session is not None:
                        session_statuses[str(session)] = False

            status = "PARCIAL" if rejected else "CONCLUIDA"
            finished_at = datetime.now(UTC)
            self._finish_execution(
                execution_id, status, finished_at, 1, processed + rejected
            )
            for session_key, successful in session_statuses.items():
                self._set_session_processing_status(
                    session_key, "CONCLUIDA" if successful else "PARCIAL"
                )
            self._db().execute("COMMIT")
        except Exception as exc:
            self._db().execute("ROLLBACK")
            self._finish_execution(
                execution_id, "FALHA", datetime.now(UTC), 1, processed, str(exc)
            )
            raise
        return TransformationResult(
            execution_id, endpoint_name, status, processed, rejected
        )

    def transform_refined(
        self, endpoint: str | None = None
    ) -> list[TransformationResult]:
        """Valida RAW, normaliza valores e grava dimensões/fatos REFINED."""
        self._db()
        endpoints = [self._endpoint(endpoint)[0]] if endpoint else list(ENDPOINTS)
        return [self._transform_endpoint(name) for name in endpoints]
