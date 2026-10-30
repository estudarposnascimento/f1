CREATE OR REPLACE VIEW gold.indicador_abandonos AS
SELECT
    ano_referencia,
    driver_number,
    COUNT(*) FILTER (WHERE dnf) AS abandonos,
    COUNT(*) FILTER (WHERE NOT dns) AS largadas,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE dnf)
            / NULLIF(COUNT(*) FILTER (WHERE NOT dns), 0),
        2
    ) AS taxa_abandono_pct
FROM gold.resultados_corrida
GROUP BY ano_referencia, driver_number;
