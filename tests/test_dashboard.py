from streamlit.testing.v1 import AppTest


def test_dashboard_handles_unavailable_database(monkeypatch):
    monkeypatch.setenv("POSTGRES_USER", "test")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test")
    monkeypatch.setenv("POSTGRES_DB", "test")
    import src.database
    def unavailable():
        raise ConnectionError("Banco indisponível no teste")
    monkeypatch.setattr(src.database, "get_engine", unavailable)
    from src.config import ROOT
    app = AppTest.from_file(ROOT / "dashboard.py").run(timeout=15)
    assert not app.exception
    assert len(app.error) == 1
    assert "PostgreSQL" in app.error[0].value
