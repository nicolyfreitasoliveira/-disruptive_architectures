CREATE TABLE IF NOT EXISTS ingestion_runs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    file_name TEXT NOT NULL,
    sha256 CHAR(64) NOT NULL UNIQUE,
    row_count BIGINT NOT NULL DEFAULT 0,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS temperature_readings (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ingestion_id BIGINT NOT NULL REFERENCES ingestion_runs(id),
    source_row BIGINT NOT NULL,
    source_id TEXT,
    device_id TEXT NOT NULL,
    recorded_at TIMESTAMP NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    location TEXT,
    UNIQUE (ingestion_id, source_row)
);
CREATE INDEX IF NOT EXISTS ix_readings_time ON temperature_readings(recorded_at);
CREATE INDEX IF NOT EXISTS ix_readings_device ON temperature_readings(device_id);
