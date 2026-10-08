import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import text

from src.database import get_engine

st.set_page_config(page_title="Temperaturas IoT", page_icon="🌡️", layout="wide")
st.title("Dashboard de Temperaturas IoT")
st.caption("Fonte: Temperature Readings: IoT Devices (Kaggle). Horários originais, sem conversão de fuso.")


@st.cache_resource
def database():
    return get_engine()


@st.cache_data(ttl=60)
def load_data():
    queries = {
        "average": "SELECT * FROM avg_temp_por_dispositivo ORDER BY device_id",
        "hour": "SELECT * FROM leituras_por_hora ORDER BY hora",
        "daily": "SELECT * FROM temp_max_min_por_dia ORDER BY data",
    }
    with database().connect() as connection:
        return {key: pd.read_sql(text(query), connection) for key, query in queries.items()}


if st.sidebar.button("Atualizar dados"):
    load_data.clear()

try:
    data = load_data()
except Exception:
    st.error("Não foi possível consultar o PostgreSQL. Configure .env, inicie o Docker e execute python -m src.pipeline.")
    st.stop()

if data["average"].empty:
    st.info("Nenhuma leitura disponível. Importe o CSV real com python -m src.pipeline.")
    st.stop()

left, middle, right = st.columns(3)
left.metric("Leituras", f'{int(data["average"]["contagem"].sum()):,}')
middle.metric("Salas/identificadores da fonte", len(data["average"]))
right.metric("Dias com leituras", len(data["daily"]))

st.header("Média de Temperatura por Dispositivo")
st.caption("O agrupamento utiliza room_id/id, identificador da sala na fonte. O dataset não fornece um identificador individual de sensor físico. A média reúne leituras In e Out.")
st.plotly_chart(px.bar(data["average"], x="device_id", y="avg_temp", labels={"device_id": "Sala (room_id/id)", "avg_temp": "Temperatura média (unidade não confirmada)"}), use_container_width=True)
st.header("Leituras por Hora do Dia")
st.caption("Contagem por hora do dia (0 a 23), somando todo o período registrado.")
st.plotly_chart(px.line(data["hour"], x="hora", y="contagem", markers=True, labels={"hora": "Hora do dia", "contagem": "Leituras"}), use_container_width=True)
st.header("Temperaturas Máximas e Mínimas por Dia")
st.caption("Extremos de todas as leituras In e Out por data. Os pontos indicam dias com registros; os segmentos não representam medições nos dias sem registros. A unidade de temp não foi confirmada na documentação da fonte.")
st.plotly_chart(px.line(data["daily"], x="data", y=["temp_max", "temp_min"], markers=True, labels={"data": "Data", "value": "Temperatura (unidade não confirmada)", "variable": "Medida"}), use_container_width=True)
with st.expander("Consultar resultados das views"):
    for name, frame in data.items():
        st.dataframe(frame, use_container_width=True)
        st.download_button(f"Baixar {name} em CSV", frame.to_csv(index=False).encode("utf-8"), f"{name}.csv", "text/csv", key=name)
