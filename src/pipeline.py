import argparse
import hashlib
import json
import os

import pandas as pd
from sqlalchemy import text

from src.config import csv_path
from src.database import get_engine, initialize
from src.processing import normalize


def ingest(path, engine, chunk_size=10000):
    if not path.is_file():
        raise FileNotFoundError(f"CSV não encontrado: {path}. Baixe a base real do Kaggle.")
    if chunk_size < 1:
        raise ValueError("CSV_CHUNK_SIZE deve ser positivo.")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    checksum = digest.hexdigest()
    # Uma única transação: qualquer erro desfaz toda a importação.
    with engine.begin() as connection:
        initialize(connection)
        run_id = connection.execute(text("""
            INSERT INTO ingestion_runs(file_name, sha256) VALUES (:name, :sha)
            ON CONFLICT (sha256) DO NOTHING RETURNING id
        """), {"name": path.name, "sha": checksum}).scalar()
        if run_id is None:
            return {"status": "já importado", "sha256": checksum}
        total = 0
        for chunk in pd.read_csv(path, chunksize=chunk_size, dtype=str, encoding="utf-8-sig"):
            rows = normalize(chunk)
            rows["ingestion_id"] = run_id
            rows["source_row"] = range(total + 1, total + len(rows) + 1)
            rows.to_sql("temperature_readings", connection, if_exists="append", index=False,
                        method="multi", chunksize=1000)
            total += len(rows)
        if total == 0:
            raise ValueError("CSV sem leituras.")
        connection.execute(text("UPDATE ingestion_runs SET row_count=:n WHERE id=:id"), {"n": total, "id": run_id})
        actual = connection.execute(text("SELECT COUNT(*) FROM temperature_readings WHERE ingestion_id=:id"), {"id": run_id}).scalar_one()
        if actual != total:
            raise RuntimeError("Contagem inserida diverge do CSV.")
    return {"status": "importado", "leituras": total, "sha256": checksum}


def main():
    parser = argparse.ArgumentParser(description="Importa leituras reais de temperatura.")
    parser.add_argument("--csv", type=str)
    args = parser.parse_args()
    from pathlib import Path
    engine = None
    try:
        path = Path(args.csv) if args.csv else csv_path()
        if not path.is_file():
            raise FileNotFoundError(f"CSV não encontrado: {path}")
        engine = get_engine()
        print(json.dumps(ingest(path, engine, int(os.getenv("CSV_CHUNK_SIZE", "10000"))), ensure_ascii=False))
    except Exception as error:
        # Erros de conexão não expõem credenciais da URL.
        print(f"Falha no pipeline: {type(error).__name__}. " + (str(error) if isinstance(error, (ValueError, FileNotFoundError)) else "Confira PostgreSQL, .env e permissões."))
        raise SystemExit(1)
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    main()
