CREATE OR REPLACE VIEW gold.resultados_corrida AS
WITH resultados AS (
    SELECT * EXCLUDE (ordem)
    FROM (
        SELECT *, ROW_NUMBER() OVER (
            PARTITION BY session_key, driver_number
            ORDER BY data_processamento DESC
        ) AS ordem
        FROM refined.fato_resultados
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
    gp.meeting_key,
    gp.meeting_name,
    sess.session_key,
    res.driver_number,
    res.position AS posicao_final,
    res.dnf,
    res.dns,
    res.dsq
FROM resultados AS res
JOIN sessoes AS sess ON sess.session_key = res.session_key
JOIN grandes_premios AS gp ON gp.meeting_key = sess.meeting_key
WHERE lower(trim(sess.session_name)) = 'race'
    AND NOT coalesce(sess.is_cancelled, FALSE);
