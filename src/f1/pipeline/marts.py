"""Views e agregações analíticas da camada de marts."""

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from f1.pipeline.refined import RefinedLayer


class MartsLayer(RefinedLayer):
    """Materializa consultas de negócio a partir das tabelas REFINED."""

    def build_gold(self) -> bool:
        """Cria a visão de resumo e executa os indicadores SQL de GOLD."""
        required_tables = {
            "dim_grandes_premios",
            "dim_sessoes",
            "fato_voltas",
            "fato_resultados",
        }
        available_tables = {
            row[0]
            for row in self._db()
            .execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'refined'"
            )
            .fetchall()
        }
        execution_id = str(uuid4())
        started_at = datetime.now(UTC)
        self._start_execution(execution_id, "GOLD", started_at)
        if not required_tables.issubset(available_tables):
            self._finish_execution(execution_id, "SEM_DADOS", datetime.now(UTC), 1, 0)
            return False

        sql_directory = Path(__file__).resolve().parents[3] / "sql" / "gold"
        indicator_files = [
            "resultados_corrida.sql",
            "indicador_vitorias.sql",
            "indicador_podios.sql",
            "indicador_abandonos.sql",
            "indicador_voltas_mais_rapidas.sql",
            (
                "indicador_paradas_box.sql"
                if "fato_pit_stops" in available_tables
                else "indicador_paradas_box_sem_dados.sql"
            ),
        ]

        try:
            self._db().execute("BEGIN TRANSACTION")
            self._db().execute(
                """
                CREATE OR REPLACE VIEW gold.resumo_piloto_sessao AS
                WITH grandes_premios AS (
                    SELECT * EXCLUDE (ordem)
                    FROM (
                        SELECT *, ROW_NUMBER() OVER (
                            PARTITION BY meeting_key ORDER BY data_processamento DESC
                        ) AS ordem
                        FROM refined.dim_grandes_premios
                    )
                    WHERE ordem = 1
                ), sessoes AS (
                    SELECT * EXCLUDE (ordem)
                    FROM (
                        SELECT *, ROW_NUMBER() OVER (
                            PARTITION BY session_key ORDER BY data_processamento DESC
                        ) AS ordem
                        FROM refined.dim_sessoes
                    )
                    WHERE ordem = 1
                ), voltas AS (
                    SELECT
                        session_key,
                        driver_number,
                        COUNT(*) FILTER (WHERE lap_duration IS NOT NULL) AS voltas_validas,
                        MIN(lap_duration) AS melhor_volta_segundos,
                        AVG(lap_duration) AS media_volta_segundos
                    FROM refined.fato_voltas
                    GROUP BY session_key, driver_number
                ), resultados AS (
                    SELECT * EXCLUDE (ordem)
                    FROM (
                        SELECT *, ROW_NUMBER() OVER (
                            PARTITION BY session_key, driver_number
                            ORDER BY data_processamento DESC
                        ) AS ordem
                        FROM refined.fato_resultados
                    )
                    WHERE ordem = 1
                )
                SELECT
                    gp.year AS ano_referencia,
                    gp.meeting_key,
                    gp.meeting_name,
                    sess.session_key,
                    sess.session_name,
                    voltas.driver_number,
                    voltas.voltas_validas,
                    voltas.melhor_volta_segundos,
                    voltas.media_volta_segundos,
                    resultados.position AS posicao_final,
                    resultados.dnf,
                    resultados.dns,
                    resultados.dsq
                FROM voltas
                JOIN sessoes AS sess USING (session_key)
                JOIN grandes_premios AS gp USING (meeting_key)
                LEFT JOIN resultados
                    ON resultados.session_key = voltas.session_key
                    AND resultados.driver_number = voltas.driver_number
                """
            )
            for sql_file in indicator_files:
                script = (sql_directory / sql_file).read_text(encoding="utf-8")
                for statement in self._db().extract_statements(script):
                    self._db().execute(statement)

            total_records = (
                self._db()
                .execute("SELECT COUNT(*) FROM gold.resultados_corrida")
                .fetchone()[0]
            )
            self._finish_execution(
                execution_id,
                "CONCLUIDA",
                datetime.now(UTC),
                len(indicator_files) + 1,
                total_records,
            )
            self._db().execute("COMMIT")
        except Exception as exc:
            self._db().execute("ROLLBACK")
            self._finish_execution(
                execution_id,
                "FALHA",
                datetime.now(UTC),
                len(indicator_files) + 1,
                0,
                str(exc),
            )
            raise
        return True
