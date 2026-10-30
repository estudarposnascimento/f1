import pytest

from f1.analytics import F1AnalyticsPipeline
from f1.pipeline.common import ENDPOINTS
from tests.conftest import (
    SAMPLE_CAR_DATA,
    SAMPLE_DRIVER,
    SAMPLE_LAP,
    SAMPLE_MEETING,
    SAMPLE_PIT,
    SAMPLE_SESSION,
    SAMPLE_SESSION_RESULT,
)


@pytest.fixture
def pipeline(tmp_path):
    with F1AnalyticsPipeline(tmp_path / "formula1.duckdb") as analytics:
        yield analytics


def test_initialize_creates_required_schemas_and_metadata(pipeline):
    schemas = {
        row[0]
        for row in pipeline._connection.execute(
            "SELECT schema_name FROM information_schema.schemata"
        ).fetchall()
    }
    metadata_tables = {
        row[0]
        for row in pipeline._connection.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'metadata'"
        ).fetchall()
    }

    assert {"raw", "metadata", "refined", "gold"}.issubset(schemas)
    assert {
        "execucoes",
        "historico_extracoes",
        "controle_sessoes",
    }.issubset(metadata_tables)
    assert len(ENDPOINTS) == 18


def test_raw_is_append_only_and_empty_extractions_are_not_fabricated(pipeline):
    first = pipeline.ingest_raw("/v1/car_data", [SAMPLE_CAR_DATA], year_reference=2024)
    second = pipeline.ingest_raw("car_data", [SAMPLE_CAR_DATA], year_reference=2024)
    raw_rows = pipeline._connection.execute(
        """
         SELECT speed, ano_referencia, json_type(payload_original),
             json_extract_string(payload_original, '$.date'), hash_conteudo
         FROM raw.telemetria_carros
         """
    ).fetchall()

    assert first.status == second.status == "CONCLUIDA"
    assert len(raw_rows) == 2
    assert raw_rows[0][:4] == (315, 2024, "OBJECT", SAMPLE_CAR_DATA["date"])
    assert raw_rows[0][4] == raw_rows[1][4]

    empty = pipeline.ingest_raw("sessions", [], session_key=9999, meeting_key=1000)
    raw_session_table = pipeline._connection.execute(
        """
		SELECT 1 FROM information_schema.tables
		WHERE table_schema = 'raw' AND table_name = 'sessoes'
		"""
    ).fetchone()
    session_status = pipeline._connection.execute(
        "SELECT status_processamento FROM metadata.controle_sessoes "
        "WHERE session_key = '9999'"
    ).fetchone()

    assert empty.status == "SEM_DADOS"
    assert empty.records_written == 0
    assert raw_session_table is None
    assert session_status == ("SEM_DADOS",)


def test_refined_is_idempotent_and_gold_summarizes_session(pipeline):
    meeting = dict(SAMPLE_MEETING)
    session = dict(SAMPLE_SESSION, meeting_key=meeting["meeting_key"])
    driver = dict(
        SAMPLE_DRIVER,
        meeting_key=meeting["meeting_key"],
        session_key=session["session_key"],
    )
    lap = dict(
        SAMPLE_LAP,
        driver_number=driver["driver_number"],
        meeting_key=meeting["meeting_key"],
        session_key=session["session_key"],
    )
    result = dict(
        SAMPLE_SESSION_RESULT,
        driver_number=driver["driver_number"],
        meeting_key=meeting["meeting_key"],
        session_key=session["session_key"],
    )

    for endpoint, payload in (
        ("meetings", meeting),
        ("sessions", session),
        ("drivers", driver),
        ("laps", lap),
        ("session_result", result),
    ):
        pipeline.ingest_raw(endpoint, [payload], year_reference=2024)

    transformations = pipeline.transform_refined()
    assert all(
        item.status == "CONCLUIDA" for item in transformations if item.records_processed
    )
    before = pipeline._connection.execute(
        "SELECT COUNT(*) FROM refined.fato_voltas"
    ).fetchone()[0]
    pipeline.transform_refined("laps")
    after = pipeline._connection.execute(
        "SELECT COUNT(*) FROM refined.fato_voltas"
    ).fetchone()[0]

    assert before == after == 1
    assert (
        pipeline._connection.execute(
            "SELECT typeof(date_start) FROM refined.fato_voltas"
        ).fetchone()[0]
        == "TIMESTAMP WITH TIME ZONE"
    )
    assert pipeline.build_gold()
    assert (
        pipeline._connection.execute(
            "SELECT COUNT(*) FROM gold.indicador_paradas_box"
        ).fetchone()[0]
        == 0
    )
    gold_row = pipeline._connection.execute(
        """
         SELECT meeting_name, session_name, driver_number,
             melhor_volta_segundos, posicao_final
         FROM gold.resumo_piloto_sessao
         """
    ).fetchone()
    assert gold_row == (
        meeting["meeting_name"],
        session["session_name"],
        driver["driver_number"],
        lap["lap_duration"],
        result["position"],
    )

    changed_driver = dict(driver, full_name="Max VERSTAPPEN Atualizado")
    pipeline.ingest_raw("drivers", [changed_driver], year_reference=2024)
    pipeline.transform_refined("drivers")
    pilot_versions = pipeline._connection.execute(
        """
         SELECT COUNT(*), COUNT(*) FILTER (WHERE versao_atual),
             COUNT(*) FILTER (WHERE valido_ate IS NOT NULL)
         FROM refined.dim_pilotos
         """
    ).fetchone()
    assert pilot_versions == (2, 1, 1)


def test_invalid_refined_records_are_saved_as_rejections(pipeline):
    invalid_lap = dict(SAMPLE_LAP, driver_number="invalid")
    pipeline.ingest_raw("laps", [invalid_lap])

    result = pipeline.transform_refined("laps")[0]
    rejection = pipeline._connection.execute(
        """
         SELECT endpoint_origem, campo_rejeitado,
             json_type(registro_original), json_extract_string(registro_original, '$.driver_number')
         FROM refined.rejeicoes
         """
    ).fetchone()

    assert result.status == "PARCIAL"
    assert result.records_processed == 0
    assert result.records_rejected == 1
    assert rejection[0] == "laps"
    assert rejection[1] == "driver_number"
    assert rejection[2] == "OBJECT"
    assert rejection[3] == "invalid"


def test_refined_rejects_records_without_a_session_dimension(pipeline):
    pipeline.ingest_raw("laps", [SAMPLE_LAP])

    result = pipeline.transform_refined("laps")[0]
    rejection = pipeline._connection.execute(
        "SELECT motivo_rejeicao FROM refined.rejeicoes"
    ).fetchone()[0]

    assert result.status == "PARCIAL"
    assert result.records_processed == 0
    assert result.records_rejected == 1
    assert "dimensão de sessões" in rejection.lower()


def test_build_gold_creates_five_sql_indicators(pipeline):
    meeting = dict(SAMPLE_MEETING)
    session = dict(
        SAMPLE_SESSION,
        meeting_key=meeting["meeting_key"],
        session_key=99001,
        session_name="Race",
        session_type="Race",
    )
    driver = dict(
        SAMPLE_DRIVER,
        meeting_key=meeting["meeting_key"],
        session_key=session["session_key"],
    )
    lap = dict(
        SAMPLE_LAP,
        driver_number=driver["driver_number"],
        meeting_key=meeting["meeting_key"],
        session_key=session["session_key"],
    )
    result = dict(
        SAMPLE_SESSION_RESULT,
        driver_number=driver["driver_number"],
        meeting_key=meeting["meeting_key"],
        session_key=session["session_key"],
        position=1,
        dnf=False,
        dns=False,
    )
    pit_stop = dict(
        SAMPLE_PIT,
        driver_number=driver["driver_number"],
        meeting_key=meeting["meeting_key"],
        session_key=session["session_key"],
    )

    for endpoint, payload in (
        ("meetings", meeting),
        ("sessions", session),
        ("drivers", driver),
        ("laps", lap),
        ("session_result", result),
        ("pit", pit_stop),
    ):
        pipeline.ingest_raw(endpoint, [payload], year_reference=2024)

    pipeline.transform_refined()
    assert pipeline.build_gold()

    indicator_views = {
        "indicador_vitorias",
        "indicador_podios",
        "indicador_abandonos",
        "indicador_voltas_mais_rapidas",
        "indicador_paradas_box",
    }
    available_views = {
        row[0]
        for row in pipeline._connection.execute(
            "SELECT table_name FROM information_schema.views "
            "WHERE table_schema = 'gold'"
        ).fetchall()
    }
    assert indicator_views.issubset(available_views)

    victories = pipeline._connection.execute(
        "SELECT vitorias FROM gold.indicador_vitorias "
        "WHERE ano_referencia = 2024 AND driver_number = 1"
    ).fetchone()
    podiums = pipeline._connection.execute(
        "SELECT podios, taxa_podio_pct FROM gold.indicador_podios "
        "WHERE ano_referencia = 2024 AND driver_number = 1"
    ).fetchone()
    abandonments = pipeline._connection.execute(
        "SELECT abandonos, taxa_abandono_pct FROM gold.indicador_abandonos "
        "WHERE ano_referencia = 2024 AND driver_number = 1"
    ).fetchone()
    fastest_lap = pipeline._connection.execute(
        "SELECT voltas_mais_rapidas, melhor_volta_temporada_segundos "
        "FROM gold.indicador_voltas_mais_rapidas "
        "WHERE ano_referencia = 2024 AND driver_number = 1"
    ).fetchone()
    pit_stops = pipeline._connection.execute(
        "SELECT paradas_com_tempo, tempo_medio_parada_segundos "
        "FROM gold.indicador_paradas_box "
        "WHERE ano_referencia = 2024 AND driver_number = 1"
    ).fetchone()

    assert victories == (1,)
    assert podiums == (1, 100.0)
    assert abandonments == (0, 0.0)
    assert fastest_lap == (1, lap["lap_duration"])
    assert pit_stops == (1, pit_stop["stop_duration"])
