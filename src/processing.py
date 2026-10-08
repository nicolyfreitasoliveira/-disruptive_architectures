"""Normalização estrita; nunca gera ou substitui leituras ausentes."""
import pandas as pd


def normalize(frame):
    frame = frame.copy()
    frame.columns = [str(c).strip().lower() for c in frame.columns]
    if frame.columns.duplicated().any():
        raise ValueError("CSV possui nomes de colunas duplicados.")
    aliases = {"room_id/id": "device_id", "noted_date": "recorded_at", "temp": "temperature", "out/in": "location", "id": "source_id"}
    frame = frame.rename(columns=aliases)
    if frame.columns.duplicated().any():
        raise ValueError("Colunas conflitantes após normalização.")
    required = {"device_id", "recorded_at", "temperature"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError("Colunas obrigatórias ausentes: " + ", ".join(sorted(missing)))
    dates = frame["recorded_at"].astype("string").str.strip()
    # O Kaggle utiliza dia-mês-ano. ISO também é aceito explicitamente.
    parsed = pd.to_datetime(dates, format="%d-%m-%Y %H:%M", errors="coerce")
    iso = dates.str.match(r"^\d{4}-\d{2}-\d{2}", na=False)
    parsed.loc[iso] = pd.to_datetime(dates.loc[iso], format="ISO8601", errors="coerce")
    frame["recorded_at"] = parsed
    frame["temperature"] = pd.to_numeric(frame["temperature"], errors="coerce")
    frame["device_id"] = frame["device_id"].astype("string").str.strip()
    invalid = (frame["recorded_at"].isna() | frame["temperature"].isna()
               | frame["temperature"].isin([float("inf"), float("-inf")])
               | frame["device_id"].isna() | frame["device_id"].eq(""))
    if invalid.any():
        raise ValueError(f"{int(invalid.sum())} leituras inválidas; índices: {frame.index[invalid].tolist()[:10]}")
    for col in ("source_id", "location"):
        if col not in frame:
            frame[col] = None
    return frame[["source_id", "device_id", "recorded_at", "temperature", "location"]]
