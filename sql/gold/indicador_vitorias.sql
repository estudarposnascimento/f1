CREATE OR REPLACE VIEW gold.indicador_vitorias AS
SELECT
    ano_referencia,
    driver_number,
    COUNT(*) FILTER (WHERE posicao_final = 1) AS vitorias,
    COUNT(*) FILTER (WHERE NOT dns) AS largadas
FROM gold.resultados_corrida
GROUP BY ano_referencia, driver_number;
