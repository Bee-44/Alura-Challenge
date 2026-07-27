# TradeMetrics AI

Journal de trading con un agente de IA que responde preguntas en lenguaje natural sobre las operaciones registradas, construido con Streamlit, LangChain y Gemini.

Este proyecto cumple el desafío final **"Alura Agente"**: (1) lee y procesa un documento CSV, (2) responde preguntas sobre él con un agente de IA basado en datos reales, y (3) queda desplegado públicamente en Oracle Cloud (OCI).

---

## Arquitectura

```
app.py              Streamlit: KPIs, formulario, chat, tabla. Solo orquesta — cero lógica de negocio.
src/data_loader.py   Esquema, carga, validación y append de operaciones (Pandas).
src/metrics.py       Funciones puras sobre DataFrame: win rate, PnL, profit factor, mindset, patrones.
src/agent.py         Agente LangChain (create_agent) + Gemini; envuelve metrics.py como @tools.
tests/test_metrics.py  Pruebas pytest sobre DataFrames sintéticos.
data/sample_journal.csv  18 operaciones ficticias de ejemplo.
docs/screenshots/    Evidencia de pruebas locales y del deploy en OCI.
```

### Flujo de datos

```
CSV (data/sample_journal.csv)
        │
        ▼
data_loader.cargar_journal()  ── valida esquema, castea tipos
        │
        ▼
metrics.py  ── win_rate, pnl_total, profit_factor, desempeno_por_mindset, detectar_patrones
        │
        ├──► app.py (KPIs + tabla "Recent Entries")
        │
        └──► agent.py ── tools que releen el CSV en cada llamada
                    │
                    ▼
              Gemini (LangChain create_agent)
                    │
                    ▼
              Respuesta en lenguaje natural (chat de Streamlit)
```

**Decisión clave:** las tools de `agent.py` releen el CSV en cada llamada, así el agente ve de inmediato cualquier operación registrada desde Streamlit, sin reconstruirse.

**Anti-alucinación:** el agente nunca calcula cifras por su cuenta — todos los números provienen de tools que ejecutan Pandas. Su *system prompt* le prohíbe inventar datos y lo obliga a responder "no tengo ese dato" si ninguna tool lo cubre.

---

## Ejemplos reales de preguntas y respuestas

Capturados durante las pruebas locales (ver `docs/screenshots/`):

> **¿Cuál fue mi win rate en octubre de 2025?**
> Tu win rate en octubre de 2025 fue del **66.67%** (6 operaciones totales, PnL total de $178 y un profit factor de 2.62).

> **¿Cuál es mi total de operaciones y mi PnL total ahora?** *(tras registrar una operación nueva en vivo)*
> Actualmente tienes un total de **19 operaciones** y un PnL total de **$387** (con un win rate general de 57.89% y un profit factor de 2.40).

> **¿Algún consejo para mi próxima operación?**
> Aquí tienes el análisis de tus patrones actuales antes de tu próxima operación:
> - Racha actual: 2 operaciones ganadoras consecutivas.
> - Mindset con peor PnL: FOMO.
> - Activo más rentable: PYPL.
> - Activo menos rentable: XOM.
>
> **Cuidado con operar por impulso o por miedo a perderte un movimiento (FOMO).** Los datos muestran claramente que las decisiones tomadas bajo el estado emocional de FOMO representan tu peor rendimiento y donde más capital pierdes. No entres al mercado persiguiendo el precio ni rompas tus reglas solo por haber tenido una racha ganadora reciente. Asegúrate de que tu próxima operación cumpla estrictamente con tu plan de trading, con un punto de entrada validado y sin emociones de por medio.

---

## Instalación y ejecución local

Requiere Python 3.11+.

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Ejecuta las pruebas:

```bash
pytest -q
```

Levanta la aplicación:

```bash
streamlit run app.py
```

Abre `http://localhost:8501` en el navegador.

---

## Deploy

El deploy se realiza en una instancia Compute de Oracle Cloud (OCI).
