CREATE OR REPLACE VIEW avg_temp_por_dispositivo AS
SELECT device_id, AVG(temperature) AS avg_temp, COUNT(*) AS contagem
FROM temperature_readings GROUP BY device_id;

-- Agrupa a hora do dia (0 a 23) em todo o período, sem conversão de fuso.
CREATE OR REPLACE VIEW leituras_por_hora AS
SELECT EXTRACT(HOUR FROM recorded_at)::INTEGER AS hora, COUNT(*) AS contagem
FROM temperature_readings GROUP BY hora;

CREATE OR REPLACE VIEW temp_max_min_por_dia AS
SELECT recorded_at::DATE AS data, MAX(temperature) AS temp_max,
       MIN(temperature) AS temp_min
FROM temperature_readings GROUP BY recorded_at::DATE;
