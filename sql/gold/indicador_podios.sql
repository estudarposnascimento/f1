CREATE OR REPLACE VIEW gold.indicador_podios AS
SELECT
    ano_referencia,
    driver_number,
    COUNT(*) FILTER (WHERE posicao_final BETWEEN 1 AND 3) AS podios,
    COUNT(*) FILTER (WHERE NOT dns) AS largadas,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE posicao_final BETWEEN 1 AND 3)
            / NULLIF(COUNT(*) FILTER (WHERE NOT dns), 0),
        2
    ) AS taxa_podio_pct
FROM gold.resultados_corrida
GROUP BY ano_referencia, driver_number;
