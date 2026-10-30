CREATE OR REPLACE VIEW gold.indicador_voltas_mais_rapidas AS
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
), melhor_volta_piloto AS (
    SELECT
        gp.year AS ano_referencia,
        lap.session_key,
        lap.driver_number,
        MIN(lap.lap_duration) AS melhor_volta_sessao_segundos
    FROM refined.fato_voltas AS lap
    JOIN sessoes AS sess USING (session_key)
    JOIN grandes_premios AS gp ON gp.meeting_key = sess.meeting_key
    WHERE lower(trim(sess.session_name)) = 'race'
        AND lap.lap_duration IS NOT NULL
    GROUP BY gp.year, lap.session_key, lap.driver_number
), melhor_volta_corrida AS (
    SELECT
        session_key,
        MIN(melhor_volta_sessao_segundos) AS melhor_volta_corrida_segundos
    FROM melhor_volta_piloto
    GROUP BY session_key
)
SELECT
    piloto.ano_referencia,
    piloto.driver_number,
    MIN(piloto.melhor_volta_sessao_segundos)
        AS melhor_volta_temporada_segundos,
    COUNT(*) FILTER (
        WHERE piloto.melhor_volta_sessao_segundos
            = corrida.melhor_volta_corrida_segundos
    ) AS voltas_mais_rapidas
FROM melhor_volta_piloto AS piloto
JOIN melhor_volta_corrida AS corrida USING (session_key)
GROUP BY piloto.ano_referencia, piloto.driver_number;
