from pathlib import Path
import pandas as pd
import pytest
from src.config import ROOT
from src.processing import normalize

CSV = ROOT / "data/IOT-temp.csv"


@pytest.mark.skipif(not CSV.is_file(), reason="CSV real não disponível")
def test_real_csv_complete_and_chunked():
    full = normalize(pd.read_csv(CSV, dtype=str))
    chunks = pd.concat([normalize(chunk) for chunk in pd.read_csv(CSV, dtype=str, chunksize=10000)])
    pd.testing.assert_frame_equal(full, chunks)
    assert len(full) > 0
    assert full.recorded_at.notna().all()
    assert full.temperature.notna().all()


@pytest.mark.skipif(not CSV.is_file(), reason="CSV real não disponível")
def test_dashboard_charts_with_real_csv(monkeypatch):
    # Exercita a UI com agregações reais em pandas, sem alegar consulta PostgreSQL.
    from streamlit.testing.v1 import AppTest
    import src.database
    frame = normalize(pd.read_csv(CSV, dtype=str))
    average = frame.groupby("device_id").temperature.agg(avg_temp="mean", contagem="size").reset_index()
    hour = frame.groupby(frame.recorded_at.dt.hour).size().rename_axis("hora").reset_index(name="contagem")
    daily = frame.groupby(frame.recorded_at.dt.date).temperature.agg(temp_max="max", temp_min="min").rename_axis("data").reset_index()
    class FakeEngine:
        def connect(self):
            from contextlib import nullcontext
            return nullcontext(None)
    monkeypatch.setattr(src.database, "get_engine", lambda: FakeEngine())
    def read_sql(query, connection):
        query = str(query)
        if "avg_temp_por_dispositivo" in query:
            return average
        if "leituras_por_hora" in query:
            return hour
        return daily
    monkeypatch.setattr(pd, "read_sql", read_sql)
    import streamlit as st
    st.cache_resource.clear()
    st.cache_data.clear()
    app = AppTest.from_file(ROOT / "dashboard.py").run(timeout=20)
    assert not app.exception
    assert not app.error
    assert len(app.get("plotly_chart")) == 3
    assert len(app.metric) == 3
    st.cache_resource.clear()
    st.cache_data.clear()
