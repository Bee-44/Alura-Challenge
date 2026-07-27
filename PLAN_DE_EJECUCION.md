# Plan de ejecución — TradeMetrics AI

## Contexto

`Product_Requirement_Document.md` especifica **TradeMetrics AI**: un journal de trading con un agente de IA que responde preguntas en lenguaje natural sobre las operaciones registradas. Es la forma personalizada de cumplir el desafío final "Alura Agente", que exige tres etapas verificables — (1) leer y procesar un documento CSV, (2) un agente que responda sobre él con datos reales, (3) deploy público en Oracle Cloud (OCI) — más un repositorio en GitHub con historial de commits progresivo y un README con arquitectura, ejemplos y evidencia del deploy.

Estado actual: la carpeta contiene únicamente `CLAUDE.md` y `Product_Requirement_Document.md`. No hay repositorio git, ni código, ni entorno virtual. Se construye desde cero siguiendo las fases 0–8 del PRD, en secuencia y sin pausas salvo las marcadas.

Entorno verificado: Python 3.11 y 3.14 instalados (`py -3.11` disponible), git 2.47 configurado como *Beatriz / beatrizdecarbonero@gmail.com*, `gh` CLI **no** instalado. En PyPI: `langchain` 1.3.x, `langchain-google-genai` 4.3.x, `streamlit` 1.60, `pandas` 3.0.

---

## Decisiones confirmadas

| Punto | Decisión |
|---|---|
| **GitHub** | La usuaria crea el repositorio vacío en github.com y entrega la URL. Yo hago `git remote add origin` y `push` en cada fase. Sin instalar `gh`. |
| **Cálculo de PnL** | Se **añade el campo `cantidad`** al modelo de datos. PnL se calcula automáticamente y el campo queda editable en el formulario. |
| **CLAUDE.md** | Se dejan ambos archivos como están. No se toca ninguno. |
| **Python** | Entorno virtual con `py -3.11` (no 3.14): el stack LangChain/Streamlit tiene soporte maduro en 3.11 y el PRD pide 3.11+. |

### Desviación documentada respecto al PRD

§3.1 define el esquema sin cantidad, lo que hace imposible un PnL monetario real. Esquema efectivo:

```
fecha, activo, direccion, precio_entrada, precio_salida, cantidad, pnl, estado_emocional, notas
```

```
pnl = (precio_salida - precio_entrada) * cantidad * (+1 si long, -1 si short)
```

Se anotará esta desviación en el README para que quede trazable frente al documento original.

---

## Arquitectura

```
app.py            Streamlit: KPIs, formulario, chat, tabla. SOLO orquesta — cero lógica de negocio.
src/data_loader.py  Esquema, carga, validación y append de operaciones (Pandas).
src/metrics.py      Funciones puras sobre DataFrame: win rate, PnL, profit factor, totales, mindset, patrones.
src/agent.py        create_agent (LangChain 1.x) + Gemini; envuelve metrics.py como @tools.
tests/test_metrics.py  pytest sobre DataFrames sintéticos.
data/sample_journal.csv
docs/screenshots/
```

**Decisión clave de diseño:** las tools de `agent.py` **releen el CSV en cada llamada** vía `data_loader.cargar_journal(ruta)`. Así, cuando la usuaria registra una operación en Streamlit, el agente la ve inmediatamente sin reconstruirse. Evita cachés desincronizadas — el archivo es pequeño y el coste es irrelevante.

**Anti-alucinación:** el agente nunca calcula aritmética por su cuenta. Todos los números provienen de tools que ejecutan Pandas. El *system prompt* le prohíbe explícitamente inventar cifras y le obliga a responder "no tengo ese dato" si ninguna tool lo cubre.

---

## Fases

Cada fase termina en commit + push y **una sola** línea de reporte pidiendo confirmación para avanzar.

### Fase 0 — Estructura inicial
1. Crear `src/`, `data/`, `tests/`, `docs/screenshots/`.
2. `.gitignore` → `.env`, `__pycache__/`, `.venv/`, `*.pyc`, `.streamlit/`.
3. `.env.example` con el formato de §3.6 (comentado, sin valores) + `GEMINI_MODEL=`.
4. Crear `.env` vacío copiando la plantilla.
5. **PAUSA (única, combinada):** pedir a la usuaria (a) escribir `GOOGLE_API_KEY` en `.env` — la obtiene en https://aistudio.google.com/app/apikey — y (b) crear el repo vacío en GitHub y entregar la URL.
6. `py -3.11 -m venv .venv`; instalar `pandas langchain langchain-google-genai streamlit python-dotenv pytest`; congelar `requirements.txt`.
7. `README.md` con título y objetivo.
8. `git init`, `git remote add origin <URL>`, commit `chore: estructura inicial del proyecto TradeMetrics AI`, push.

→ **verificar:** `.venv` activable, `pip list` muestra los 6 paquetes, `git log` con 1 commit, `.env` **no** aparece en `git status`.

### Fase 1 — Carga de datos *(Etapa 1 del desafío)*
1. `src/data_loader.py`:
   - `COLUMNAS` / `DIRECCIONES` (`long`,`short`) / `MINDSETS` (`Calm`,`Anxious`,`Confident`,`FOMO`) como constantes.
   - `cargar_journal(ruta: Path) -> pd.DataFrame` — lee CSV, parsea `fecha` a datetime, castea numéricos, valida columnas y valores permitidos, lanza `ValueError` descriptivo.
   - `calcular_pnl(entrada, salida, cantidad, direccion) -> float`.
   - `agregar_operacion(ruta, operacion: dict) -> pd.DataFrame` — valida y hace append al CSV.
2. `data/sample_journal.csv` con **18 operaciones ficticias**: tickers variados, long y short, fechas repartidas entre **septiembre y octubre 2025** (para que "¿mi win rate en octubre?" sea respondible), los 4 mindsets presentes, y un patrón deliberado — las operaciones en **FOMO** mayoritariamente perdedoras y las **Calm** mayoritariamente ganadoras, para que el motor de recomendaciones de la Fase 4 tenga algo real que detectar.
3. Ejecutar el módulo y confirmar carga limpia.
4. Commit `feat: carga y validación de datos del journal desde CSV`, push.

→ **verificar:** `python -c "from src.data_loader import cargar_journal; print(cargar_journal('data/sample_journal.csv').dtypes)"` sin errores y con 18 filas.

### Fase 2 — Métricas
1. `src/metrics.py` — funciones puras, todas reciben `df: pd.DataFrame`:
   - `win_rate(df) -> float`
   - `pnl_total(df) -> float`
   - `profit_factor(df) -> float` (maneja el caso sin pérdidas → `inf`)
   - `total_operaciones(df) -> int`
   - `desempeno_por_mindset(df) -> pd.DataFrame` (nº ops, win rate y PnL por estado emocional)
   - `filtrar_periodo(df, inicio, fin) -> pd.DataFrame` — habilita las preguntas por mes
   - `resumen(df) -> dict` — los 4 KPIs de una sola llamada
2. `tests/test_metrics.py`: DataFrame sintético fijo + casos borde (df vacío, sin operaciones perdedoras, todas perdedoras).
3. Ejecutar `pytest -q`.
4. Commit `feat: cálculo de métricas de rendimiento`, push.

→ **verificar:** `pytest -q` en verde.

### Fase 3 — Agente conversacional *(Etapa 2 del desafío)*
1. `src/agent.py`:
   - `load_dotenv()`; leer `GOOGLE_API_KEY` y `GEMINI_MODEL` con `os.getenv` — **nunca** imprimir ni loguear el valor.
   - **Verificar en ejecución** el id de modelo Gemini disponible con la API key (no fijarlo a ciegas); dejarlo configurable en `.env` con un valor por defecto ya comprobado.
   - Tools con `@tool` de `langchain.tools`, cada una releyendo el CSV: `obtener_resumen`, `metricas_por_periodo(inicio, fin)`, `analisis_por_mindset`, `listar_operaciones(n, activo, direccion)`.
   - `crear_agente(ruta_csv)` → `create_agent(model=..., tools=[...], system_prompt=..., checkpointer=InMemorySaver())` de `langchain.agents` (API de LangChain 1.x). Confirmar la superficie de API contra la versión realmente instalada antes de escribir el módulo.
   - `preguntar(agente, texto, thread_id) -> str`.
2. Probar por consola 3 preguntas: win rate global, win rate de octubre, mejor y peor operación.
3. Commit `feat: agente LangChain para consultas en lenguaje natural`, push.

→ **verificar:** las 3 respuestas coinciden con los números que devuelve `metrics.py` directamente.

### Fase 4 — Motor de recomendaciones
1. Añadir a `metrics.py`: `detectar_patrones(df) -> dict` — racha ganadora/perdedora actual, mindset con peor PnL, activo más rentable y menos rentable.
2. Exponerla como tool `detectar_patrones` y ampliar el *system prompt* con el rol de coach: observar el patrón, advertir sobre riesgo de comportamiento (exceso de confianza tras racha, operar en FOMO), tono directo y no complaciente — según §2.5.
3. Probar: "¿algún consejo para mi próxima operación?".
4. Commit `feat: motor de recomendaciones basado en patrones del journal`, push.

→ **verificar:** la respuesta cita el patrón FOMO→pérdidas que existe de verdad en los datos.

### Fase 5 — Interfaz Streamlit
1. `app.py` — sin lógica de negocio, solo orquestación:
   - Sidebar: marca "TradeMetrics AI" + navegación mínima.
   - 4 tarjetas KPI con `st.metric` desde `metrics.resumen()`.
   - Formulario `st.form` "Log New Trade": ticker, Long/Short, entrada, salida, **cantidad**, PnL prellenado y editable, mindset (Calm/Anxious/Confident/FOMO), textarea de reflexión, botón "Save Journal Entry" → `data_loader.agregar_operacion`.
   - Chat con `st.chat_message` / `st.chat_input`; agente en `st.cache_resource`, `thread_id` en `st.session_state`.
   - Tabla "Recent Entries" con `st.dataframe` (últimas N filas).
2. `streamlit run app.py` y verificar carga sin errores.
3. Commit `feat: interfaz Streamlit para registro y análisis`, push.

→ **verificar:** app abre en el navegador, KPIs con cifras reales, formulario guarda, chat responde.

### Fase 6 — Pruebas end-to-end
1. Recorrido manual: cargar CSV → ver métricas → preguntar → registrar operación nueva → volver a preguntar y confirmar que el número **cambió**.
2. Capturas en `docs/screenshots/`.
3. Commit `docs: capturas de pruebas locales end-to-end`, push.

### Fase 7 — README final
Arquitectura, diagrama de flujo, ejemplos **reales** de preguntas/respuestas (copiados de las pruebas, no inventados), instalación, configuración de `.env` desde `.env.example`, cómo ejecutar, y nota de la desviación del esquema (`cantidad`).
Commit `docs: README con arquitectura, ejemplos e instrucciones de uso`, push.

### Fase 8 — Deploy en OCI *(Etapa 3 del desafío)*
1. **PAUSA obligatoria:** confirmar antes de crear recursos reales en OCI (credenciales de nube y posible coste).
2. Guiar: instancia Compute (Ubuntu, *Always Free* si aplica) → abrir puerto 8501 en la security list **y** en el firewall del sistema → clonar repo, venv, dependencias → `.env` en el servidor con la key → servicio `systemd` para ejecución persistente.
3. Verificar acceso público desde fuera de la instancia.
4. Captura + enlace en `docs/screenshots/` y README.
5. Commit `docs: enlace y captura del deploy funcionando en OCI`, push.

---

## Verificación end-to-end (criterio de éxito global)

1. `pytest -q` → todo en verde.
2. `streamlit run app.py` → los 4 KPIs muestran las cifras de `sample_journal.csv`.
3. Preguntar "¿cuál fue mi win rate en octubre?" → la cifra coincide con `filtrar_periodo` + `win_rate` calculados a mano.
4. Registrar una operación nueva → la tabla y los KPIs se actualizan → repreguntar y confirmar que el agente refleja el cambio.
5. Preguntar "¿algún consejo?" → cita un patrón presente en los datos reales.
6. `git log --oneline` → un commit por fase, en orden, con prefijos `chore/feat/test/docs`.
7. URL pública de OCI abierta desde otro dispositivo.

## Riesgos y puntos de atención

- **Id del modelo Gemini:** se verifica contra la API real en la Fase 3 en vez de asumirlo; queda en `.env` para cambiarlo sin tocar código.
- **API de LangChain 1.x:** `create_agent` reemplaza al antiguo `AgentExecutor`. Se confirmará contra la versión instalada antes de escribir `agent.py`.
- **Secretos:** `.env` se ignora desde el primer commit, antes de que exista. Su contenido nunca se lee, imprime ni cita. En OCI la key se escribe directamente en el servidor.
- **Cuota gratuita de Gemini:** si aparecen errores de rate limit en las pruebas, se reportará en lugar de reintentar en bucle.
