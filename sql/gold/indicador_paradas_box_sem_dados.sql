CREATE OR REPLACE VIEW gold.indicador_paradas_box AS
SELECT
    CAST(NULL AS INTEGER) AS ano_referencia,
    CAST(NULL AS BIGINT) AS driver_number,
    CAST(NULL AS BIGINT) AS paradas_com_tempo,
    CAST(NULL AS DOUBLE) AS tempo_medio_parada_segundos
WHERE FALSE;
