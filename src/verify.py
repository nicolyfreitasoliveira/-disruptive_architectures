"""Verifica conexão, contagens e resultados das três views."""
from sqlalchemy import text
from src.database import get_engine


def verify(engine):
    with engine.connect() as connection:
        connection.execute(text("SELECT 1")).scalar_one()
        total = connection.execute(text("SELECT COUNT(*) FROM temperature_readings")).scalar_one()
        imported = connection.execute(text("SELECT COALESCE(SUM(row_count),0) FROM ingestion_runs")).scalar_one()
        assert total == imported, "Contagens do histórico e das leituras divergem"
        for view in ("avg_temp_por_dispositivo", "leituras_por_hora", "temp_max_min_por_dia"):
            rows = connection.execute(text(f"SELECT * FROM {view} LIMIT 3")).mappings().all()
            print(view, [dict(row) for row in rows])
        hourly = connection.execute(text("SELECT COALESCE(SUM(contagem),0) FROM leituras_por_hora")).scalar_one()
        assert hourly == total, "Contagem por hora diverge"
        print(f"Conexão OK; leituras={total}; contagens e views verificadas.")
        if not total:
            raise ValueError("Banco vazio: importe o CSV real para validar os dados.")


if __name__ == "__main__":
    engine = None
    try:
        engine = get_engine()
        verify(engine)
    except Exception as error:
        print(f"Verificação falhou: {type(error).__name__}. Confira .env, banco e importação.")
        raise SystemExit(1)
    finally:
        if engine is not None:
            engine.dispose()
