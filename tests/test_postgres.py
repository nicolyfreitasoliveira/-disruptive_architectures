"""Integração opt-in em banco de teste; fixtures nunca são persistidas."""
import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from src.database import initialize
from src.pipeline import ingest


@pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="Configure TEST_DATABASE_URL para PostgreSQL de teste")
def test_postgres_ingestion_views_and_rollback(tmp_path):
    engine = create_engine(os.environ["TEST_DATABASE_URL"])
    # Transação externa revertida ao final: não deixa dados de teste no banco.
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            import uuid
            schema = "test_" + uuid.uuid4().hex
            connection.execute(text(f'CREATE SCHEMA "{schema}"'))
            connection.execute(text(f'SET LOCAL search_path TO "{schema}"'))
            initialize(connection)
            path = tmp_path / "fixture.csv"
            path.write_text("id,room_id/id,noted_date,temp,out/in\na,room,01-02-2020 03:00,10,In\nb,room,01-02-2020 03:10,20,In\n", encoding="utf-8")
            class TransactionAdapter:
                def begin(self):
                    from contextlib import contextmanager
                    @contextmanager
                    def scope():
                        with connection.begin_nested():
                            yield connection
                    return scope()
            adapter = TransactionAdapter()
            assert ingest(path, adapter, 1)["leituras"] == 2
            assert ingest(path, adapter)["status"] == "já importado"
            assert connection.execute(text("SELECT avg_temp FROM avg_temp_por_dispositivo")).scalar_one() == 15
            assert connection.execute(text("SELECT contagem FROM leituras_por_hora WHERE hora=3")).scalar_one() == 2
            assert tuple(connection.execute(text("SELECT temp_min,temp_max FROM temp_max_min_por_dia")).one()) == (10, 20)
            bad = tmp_path / "invalid.csv"
            bad.write_text(path.read_text() + "c,room,invalid,30,In\n", encoding="utf-8")
            with pytest.raises(ValueError):
                ingest(bad, adapter, 1)
            assert connection.execute(text("SELECT COUNT(*) FROM temperature_readings")).scalar_one() == 2
        finally:
            transaction.rollback()
    engine.dispose()
