"""Auditoria somente leitura: compara cada registro e cada agregado com o CSV."""
import csv
import hashlib
import json
from datetime import datetime

import pandas as pd
from sqlalchemy import text

from src.config import ROOT, csv_path
from src.database import get_engine


def audit():
    path = csv_path()
    checksum = hashlib.sha256(path.read_bytes()).hexdigest()
    # Interpretação independente da função normalize do pipeline.
    with path.open(encoding="utf-8-sig", newline="") as handle:
        original = list(csv.DictReader(handle))
    expected = pd.DataFrame([
        {"source_row": index, "source_id": row["id"], "device_id": row["room_id/id"],
         "recorded_at": datetime.strptime(row["noted_date"], "%d-%m-%Y %H:%M"),
         "temperature": float(row["temp"]), "location": row["out/in"]}
        for index, row in enumerate(original, start=1)
    ])
    engine = get_engine()
    try:
        with engine.connect().execution_options(isolation_level="REPEATABLE READ") as connection:
            with connection.begin():
                runs = pd.read_sql(text("SELECT id, file_name, sha256, row_count FROM ingestion_runs ORDER BY id"), connection)
                actual = pd.read_sql(text("SELECT source_row, source_id, device_id, recorded_at, temperature, location FROM temperature_readings ORDER BY ingestion_id, source_row"), connection)
                average = pd.read_sql(text("SELECT * FROM avg_temp_por_dispositivo ORDER BY device_id"), connection)
                hours = pd.read_sql(text("SELECT * FROM leituras_por_hora ORDER BY hora"), connection)
                daily = pd.read_sql(text("SELECT * FROM temp_max_min_por_dia ORDER BY data"), connection)
        pd.testing.assert_frame_equal(expected, actual, check_dtype=False, check_exact=True)
        assert len(runs) == 1 and runs.iloc[0]["sha256"].strip() == checksum, "Histórico não corresponde exclusivamente ao arquivo auditado"
        assert int(runs.iloc[0]["row_count"]) == len(expected)
        expected_avg = expected.groupby("device_id").temperature.agg(avg_temp="mean", contagem="size").reset_index()
        expected_hours = expected.groupby(expected.recorded_at.dt.hour).size().rename_axis("hora").reset_index(name="contagem")
        expected_daily = expected.groupby(expected.recorded_at.dt.date).temperature.agg(temp_max="max", temp_min="min").rename_axis("data").reset_index()
        pd.testing.assert_frame_equal(expected_avg, average, check_dtype=False, rtol=1e-12, atol=1e-12)
        pd.testing.assert_frame_equal(expected_hours, hours, check_dtype=False, check_exact=True)
        pd.testing.assert_frame_equal(expected_daily, daily, check_dtype=False, check_exact=True)
        return {
            "csv": path.name, "sha256": checksum, "rows_csv": len(expected), "rows_postgresql": len(actual),
            "all_rows_equal": True, "single_matching_import": True,
            "average_view_equal": True, "hour_view_equal": True, "daily_view_equal": True,
            "days_with_readings": len(daily),
            "calendar_days_inclusive": int((expected.recorded_at.max().normalize()-expected.recorded_at.min().normalize()).days + 1),
            "room_identifiers": expected.device_id.unique().tolist(),
            "location_counts": {str(k): int(v) for k, v in expected.location.value_counts().items()},
            "unique_reading_ids": int(expected.source_id.nunique()),
            "duplicate_complete_rows": int(expected.drop(columns="source_row").duplicated().sum()),
            "average": float(average.iloc[0].avg_temp),
            "min": float(expected.temperature.min()), "max": float(expected.temperature.max()),
            "start": str(expected.recorded_at.min()), "end": str(expected.recorded_at.max()),
            "unit": "Não especificada no CSV; não confirmada na documentação primária acessível.",
            "scope": "Consultas somente leitura; comparação integral independente do processamento do pipeline.",
        }
    finally:
        engine.dispose()


if __name__ == "__main__":
    result = audit()
    output = ROOT / "docs/auditoria-postgresql.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
