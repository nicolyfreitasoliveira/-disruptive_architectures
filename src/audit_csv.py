"""Audita a base real sem depender do banco; não comprova ingestão SQL."""
import hashlib
import json
import pandas as pd
from src.config import csv_path
from src.processing import normalize


def audit(path):
    raw = pd.read_csv(path, dtype=str)
    frame = normalize(raw)
    daily = frame.groupby(frame.recorded_at.dt.date).temperature.agg(["min", "max"])
    average = frame.groupby("device_id").temperature.mean()
    hours = frame.groupby(frame.recorded_at.dt.hour).size()
    return {
        "file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "rows": len(frame), "columns": raw.columns.tolist(),
        "devices": frame.device_id.unique().tolist(),
        "locations": sorted(frame.location.dropna().unique().tolist()),
        "start": str(frame.recorded_at.min()), "end": str(frame.recorded_at.max()),
        "minimum": float(frame.temperature.min()), "maximum": float(frame.temperature.max()),
        "averages": average.to_dict(), "hour_counts": {str(k): int(v) for k, v in hours.items()},
        "days": len(daily), "largest_amplitude_day": str((daily["max"]-daily["min"]).idxmax()),
        "largest_amplitude": float((daily["max"]-daily["min"]).max()),
        "scope": "Auditoria pandas do CSV real; PostgreSQL não validado por este comando.",
    }


if __name__ == "__main__":
    print(json.dumps(audit(csv_path()), ensure_ascii=False, indent=2))
