import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def database_url():
    required = ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise ValueError("Configure .env: " + ", ".join(missing))
    return URL.create(
        "postgresql+psycopg2", username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"], host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")), database=os.environ["POSTGRES_DB"],
    )


def csv_path():
    path = Path(os.getenv("CSV_PATH", "data/IOT-temp.csv"))
    return path if path.is_absolute() else ROOT / path
