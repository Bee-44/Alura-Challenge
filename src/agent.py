"""Agente conversacional (LangChain + Gemini) sobre el journal de trading.

Las tools releen el CSV en cada llamada para que el agente siempre vea
los datos más recientes, incluyendo operaciones registradas en la sesión
de Streamlit sin necesidad de reconstruir el agente.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from src.data_loader import cargar_journal
from src.metrics import desempeno_por_mindset, filtrar_periodo, resumen
from src.metrics import detectar_patrones as _detectar_patrones

load_dotenv()

MODELO_POR_DEFECTO = "gemini-flash-lite-latest"

SYSTEM_PROMPT = """Eres el asistente de TradeMetrics AI, un coach de trading \
que responde preguntas sobre el journal de operaciones del usuario y advierte \
sobre riesgos de comportamiento antes de su próxima operación.

Reglas estrictas:
- Nunca calcules cifras (win rate, PnL, promedios, etc.) por tu cuenta. \
Todos los números deben venir de una tool.
- Si ninguna tool cubre lo que se pregunta, responde honestamente "no tengo \
ese dato" en vez de inventar una cifra.
- Sé directo y claro en tus respuestas, citando los números exactos que \
devuelven las tools.

Como coach:
- Cuando te pidan un consejo, usa la tool detectar_patrones para observar la \
racha actual, el mindset con peor rendimiento y los activos más y menos \
rentables.
- Si la racha actual es ganadora y larga, advierte sobre el riesgo de exceso \
de confianza. Si el mindset con peor pnl es FOMO, advierte explícitamente \
sobre operar por impulso o miedo a perderse un movimiento.
- Tono directo y no complaciente: prioriza señalar el riesgo real sobre \
sonar amable.
"""


def _crear_tools(ruta_csv: Path):
    @tool
    def obtener_resumen() -> dict:
        """Devuelve los KPIs globales del journal: win rate, PnL total, profit factor y total de operaciones."""
        return resumen(cargar_journal(ruta_csv))

    @tool
    def metricas_por_periodo(inicio: str, fin: str) -> dict:
        """Devuelve los KPIs del journal filtrados entre dos fechas (formato YYYY-MM-DD, inclusive)."""
        df = filtrar_periodo(cargar_journal(ruta_csv), inicio, fin)
        return resumen(df)

    @tool
    def analisis_por_mindset() -> list[dict]:
        """Devuelve número de operaciones, win rate y PnL total agrupados por estado emocional (Calm/Anxious/Confident/FOMO)."""
        df = desempeno_por_mindset(cargar_journal(ruta_csv))
        return df.to_dict(orient="records")

    @tool
    def listar_operaciones(n: int = 10, activo: str | None = None, direccion: str | None = None) -> list[dict]:
        """Lista las últimas n operaciones del journal, opcionalmente filtradas por activo (ticker) y/o dirección (long/short)."""
        df = cargar_journal(ruta_csv)
        if activo is not None:
            df = df[df["activo"] == activo]
        if direccion is not None:
            df = df[df["direccion"] == direccion]
        return df.tail(n).to_dict(orient="records")

    @tool
    def detectar_patrones() -> dict:
        """Detecta patrones de comportamiento: racha ganadora/perdedora actual, el estado emocional con peor PnL, y el activo más y menos rentable."""
        return _detectar_patrones(cargar_journal(ruta_csv))

    return [
        obtener_resumen,
        metricas_por_periodo,
        analisis_por_mindset,
        listar_operaciones,
        detectar_patrones,
    ]


def crear_agente(ruta_csv: Path):
    """Construye el agente conversacional con sus tools y memoria de conversación."""
    modelo = os.getenv("GEMINI_MODEL") or MODELO_POR_DEFECTO
    return create_agent(
        model=f"google_genai:{modelo}",
        tools=_crear_tools(ruta_csv),
        system_prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
    )


def _texto_de(contenido) -> str:
    if isinstance(contenido, str):
        return contenido
    return "".join(bloque.get("text", "") for bloque in contenido if isinstance(bloque, dict))


def preguntar(agente, texto: str, thread_id: str) -> str:
    """Envía una pregunta al agente dentro de un hilo de conversación y devuelve su respuesta en texto plano."""
    config = {"configurable": {"thread_id": thread_id}}
    resultado = agente.invoke({"messages": [{"role": "user", "content": texto}]}, config=config)
    return _texto_de(resultado["messages"][-1].content)


if __name__ == "__main__":
    agente = crear_agente(Path("data/sample_journal.csv"))
    for pregunta in [
        "¿Cuál es mi win rate global?",
        "¿Cuál fue mi win rate en octubre de 2025?",
        "¿Cuál fue mi mejor y mi peor operación?",
    ]:
        print(f"\n> {pregunta}")
        print(preguntar(agente, pregunta, thread_id="cli"))
