from sqlalchemy import create_engine, text

from src.config import ROOT, database_url


def get_engine():
    return create_engine(database_url(), pool_pre_ping=True, connect_args={"connect_timeout": 5})


def initialize(connection):
    for filename in ("schema.sql", "views.sql"):
        for statement in (ROOT / "sql" / filename).read_text(encoding="utf-8").split(";"):
            if statement.strip():
                connection.execute(text(statement))
