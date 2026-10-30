"""Conexão DuckDB, schemas e recursos comuns das camadas."""

from datetime import datetime
from pathlib import Path
from typing import Any, Self

import duckdb


class DatabaseLayer:
    """Inicializa o banco e fornece conexão e tabelas de controle compartilhadas."""

    def __init__(self, database_path: str | Path = "formula1.duckdb") -> None:
        self.database_path = Path(database_path)
        self._connection: duckdb.DuckDBPyConnection | None = None

    def initialize(self) -> None:
        """Cria o banco e os schemas de trabalho, sem apagar dados existentes."""
        if self._connection is not None:
            return

        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = duckdb.connect(str(self.database_path))

        for schema in ("raw", "metadata", "refined", "gold"):
            self._connection.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata.execucoes (
                id_execucao VARCHAR PRIMARY KEY,
                tipo_execucao VARCHAR NOT NULL,
                data_inicio TIMESTAMPTZ NOT NULL,
                data_fim TIMESTAMPTZ,
                status VARCHAR NOT NULL,
                temporadas JSON,
                total_endpoints BIGINT NOT NULL DEFAULT 0,
                total_registros BIGINT NOT NULL DEFAULT 0,
                mensagem_erro VARCHAR
            )
            """
        )
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata.historico_extracoes (
                id_extracao VARCHAR PRIMARY KEY,
                id_execucao VARCHAR NOT NULL,
                endpoint VARCHAR NOT NULL,
                meeting_key VARCHAR,
                session_key VARCHAR,
                data_inicio TIMESTAMPTZ NOT NULL,
                data_fim TIMESTAMPTZ,
                status VARCHAR NOT NULL,
                quantidade_registros BIGINT NOT NULL DEFAULT 0,
                hash_conteudo VARCHAR,
                mensagem_erro VARCHAR
            )
            """
        )
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata.controle_sessoes (
                session_key VARCHAR PRIMARY KEY,
                meeting_key VARCHAR,
                ano_referencia INTEGER,
                ultima_extracao TIMESTAMPTZ,
                ultimo_hash VARCHAR,
                status_processamento VARCHAR NOT NULL,
                data_ultima_alteracao TIMESTAMPTZ NOT NULL
            )
            """
        )
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS refined.rejeicoes (
                id_rejeicao VARCHAR PRIMARY KEY,
                id_execucao VARCHAR NOT NULL,
                endpoint_origem VARCHAR NOT NULL,
                tabela_origem VARCHAR NOT NULL,
                session_key VARCHAR,
                registro_original JSON NOT NULL,
                campo_rejeitado VARCHAR,
                valor_rejeitado JSON,
                motivo_rejeicao VARCHAR NOT NULL,
                data_rejeicao TIMESTAMPTZ NOT NULL
            )
            """
        )

    def close(self) -> None:
        """Fecha a conexão DuckDB, se estiver aberta."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> Self:
        self.initialize()
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()

    def _db(self) -> duckdb.DuckDBPyConnection:
        if self._connection is None:
            raise RuntimeError("Inicialize o pipeline antes de acessar o banco.")
        return self._connection

    def _start_execution(
        self, execution_id: str, kind: str, started_at: datetime
    ) -> None:
        self._db().execute(
            """
            INSERT INTO metadata.execucoes
                (id_execucao, tipo_execucao, data_inicio, status)
            VALUES (?, ?, ?, 'EXECUTANDO')
            """,
            [execution_id, kind, started_at],
        )

    def _finish_execution(
        self,
        execution_id: str,
        status: str,
        finished_at: datetime,
        endpoints: int,
        records: int,
        error: str | None = None,
    ) -> None:
        self._db().execute(
            """
            UPDATE metadata.execucoes
            SET data_fim = ?, status = ?, total_endpoints = ?,
                total_registros = ?, mensagem_erro = ?
            WHERE id_execucao = ?
            """,
            [finished_at, status, endpoints, records, error, execution_id],
        )

    def _record_session_status(
        self,
        session_key: Any,
        meeting_key: Any,
        year_reference: Any,
        extracted_at: datetime,
        content_hash: str | None,
        status: str,
    ) -> None:
        if session_key is None:
            return
        self._db().execute(
            """
            INSERT INTO metadata.controle_sessoes (
                session_key, meeting_key, ano_referencia, ultima_extracao,
                ultimo_hash, status_processamento, data_ultima_alteracao
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (session_key) DO UPDATE SET
                meeting_key = excluded.meeting_key,
                ano_referencia = excluded.ano_referencia,
                ultima_extracao = excluded.ultima_extracao,
                ultimo_hash = excluded.ultimo_hash,
                status_processamento = excluded.status_processamento,
                data_ultima_alteracao = excluded.data_ultima_alteracao
            """,
            [
                str(session_key),
                str(meeting_key) if meeting_key is not None else None,
                year_reference,
                extracted_at,
                content_hash,
                status,
                extracted_at,
            ],
        )

    def _refined_table_exists(self, table: str) -> bool:
        return (
            self._db()
            .execute(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_schema = 'refined' AND table_name = ?",
                [table],
            )
            .fetchone()
            is not None
        )
