"""TradeMetrics AI — interfaz Streamlit. Solo orquesta: sin lógica de negocio."""

from pathlib import Path

import pandas as pd
import streamlit as st

from src.agent import crear_agente, preguntar
from src.data_loader import DIRECCIONES, MINDSETS, agregar_operacion, calcular_pnl, cargar_journal
from src.metrics import resumen

RUTA_CSV = Path("data/sample_journal.csv")

st.set_page_config(page_title="TradeMetrics AI", layout="wide")

with st.sidebar:
    st.title("TradeMetrics AI")
    st.caption("Journal de trading con coach de IA")

df = cargar_journal(RUTA_CSV)
kpis = resumen(df)

st.header("Journal Dashboard")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Win Rate", f"{kpis['win_rate']:.1f}%")
col2.metric("Total PnL", f"${kpis['pnl_total']:,.2f}")
profit_factor_texto = "∞" if kpis["profit_factor"] == float("inf") else f"{kpis['profit_factor']:.2f}"
col3.metric("Profit Factor", profit_factor_texto)
col4.metric("Total Trades", kpis["total_operaciones"])

st.divider()

col_form, col_chat = st.columns(2)

with col_form:
    st.subheader("Log New Trade")
    with st.form("nueva_operacion", clear_on_submit=True):
        activo = st.text_input("Asset / Ticker")
        direccion = st.selectbox("Direction", DIRECCIONES)
        precio_entrada = st.number_input("Entry Price", min_value=0.0, step=0.01)
        precio_salida = st.number_input("Exit Price", min_value=0.0, step=0.01)
        cantidad = st.number_input("Quantity", min_value=0.0, step=1.0)
        pnl_sugerido = calcular_pnl(precio_entrada, precio_salida, cantidad, direccion)
        pnl = st.number_input("Result (PnL)", value=pnl_sugerido, step=0.01)
        estado_emocional = st.selectbox("Mindset & Emotional State", MINDSETS)
        notas = st.text_area(
            "What were you feeling during this trade? Was your thesis correct? Be honest with yourself."
        )
        enviado = st.form_submit_button("Save Journal Entry")

        if enviado:
            agregar_operacion(
                RUTA_CSV,
                {
                    "fecha": pd.Timestamp.now().strftime("%Y-%m-%d"),
                    "activo": activo,
                    "direccion": direccion,
                    "precio_entrada": precio_entrada,
                    "precio_salida": precio_salida,
                    "cantidad": cantidad,
                    "pnl": pnl,
                    "estado_emocional": estado_emocional,
                    "notas": notas,
                },
            )
            st.success("Operación guardada.")
            st.rerun()

with col_chat:
    st.subheader("AI Trading Assistant")

    @st.cache_resource
    def _obtener_agente():
        return crear_agente(RUTA_CSV)

    agente = _obtener_agente()
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = "streamlit-session"
    if "historial" not in st.session_state:
        st.session_state.historial = []

    for rol, mensaje in st.session_state.historial:
        with st.chat_message(rol):
            st.markdown(mensaje)

    pregunta = st.chat_input("Reflect on your thoughts...")
    if pregunta:
        st.session_state.historial.append(("user", pregunta))
        with st.chat_message("user"):
            st.markdown(pregunta)
        with st.chat_message("assistant"):
            with st.spinner("Analizando tu journal..."):
                respuesta = preguntar(agente, pregunta, st.session_state.thread_id)
            st.markdown(respuesta)
        st.session_state.historial.append(("assistant", respuesta))

st.divider()
st.subheader("Recent Entries")
st.dataframe(
    df[["fecha", "activo", "direccion", "precio_entrada", "precio_salida", "pnl", "estado_emocional"]]
    .sort_values("fecha", ascending=False)
    .head(20),
    use_container_width=True,
)
