CREATE OR REPLACE VIEW gold.indicador_paradas_box AS
WITH sessoes AS (
    SELECT * EXCLUDE (ordem)
    FROM (
        SELECT *, ROW_NUMBER() OVER (
            PARTITION BY session_key ORDER BY data_processamento DESC
        ) AS ordem
        FROM refined.dim_sessoes
    )
    WHERE ordem = 1
), grandes_premios AS (
    SELECT * EXCLUDE (ordem)
    FROM (
        SELECT *, ROW_NUMBER() OVER (
            PARTITION BY meeting_key ORDER BY data_processamento DESC
        ) AS ordem
        FROM refined.dim_grandes_premios
    )
    WHERE ordem = 1
)
SELECT
    gp.year AS ano_referencia,
    pit.driver_number,
    COUNT(*) FILTER (WHERE pit.stop_duration IS NOT NULL) AS paradas_com_tempo,
    AVG(pit.stop_duration) AS tempo_medio_parada_segundos
FROM refined.fato_pit_stops AS pit
JOIN sessoes AS sess USING (session_key)
JOIN grandes_premios AS gp ON gp.meeting_key = sess.meeting_key
WHERE lower(trim(sess.session_name)) = 'race'
GROUP BY gp.year, pit.driver_number;
