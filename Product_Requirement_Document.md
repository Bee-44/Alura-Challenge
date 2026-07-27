# CLAUDE.md — TradeMetrics AI

Este documento es el contexto operativo persistente del proyecto. Debe leerse íntegramente antes de actuar. Contiene todo lo necesario para entender el proyecto, sus requisitos de origen, el diseño de interfaz de referencia y las reglas de trabajo — el usuario no debería tener que reexplicar nada de esto en sesiones futuras.

---

## 1. Origen del proyecto: requisitos del desafío "Alura Agente"

Este proyecto es la forma personalizada de cumplir un desafío final asignado llamado **Alura Agente**. El desafío original plantea un escenario ficticio (una empresa con grandes volúmenes de documentos internos donde el personal pierde tiempo buscando información) y pide construir un agente de IA que responda preguntas en lenguaje natural sobre esos documentos. El usuario decidió reemplazar ese escenario genérico por un proyecto propio (TradeMetrics AI), pero **debe seguir cumpliendo exactamente los mismos requisitos y criterios de validación** del desafío original. Estos son:

### 1.1 Las tres etapas obligatorias
1. **Lectura y procesamiento de un documento** (PDF o CSV): escribir código que lea el archivo y "entienda" su contenido. En este proyecto, el documento es el CSV del journal de trading (registro de operaciones).
2. **Agente de IA que responde preguntas sobre ese documento**: el agente debe poder recibir una pregunta en lenguaje natural (ej. "¿cuál fue mi win rate en octubre?") y devolver una respuesta clara basada en los datos reales del documento, no en información inventada.
3. **Deploy en la nube de Oracle (OCI)**: la aplicación debe salir de la máquina local y quedar accesible públicamente, ejecutándose de verdad en la nube (sugerido: OCI Compute; el desafío permite usar otra herramienta si el usuario la domina mejor, pero por defecto se usará OCI Compute).

### 1.2 Tecnologías sugeridas por el desafío (no obligatorias, pero es la base elegida para este proyecto)
- **Python** para el código.
- **LangChain** para construir el agente.
- **PyPDF** o **Pandas** para leer documentos (aquí: Pandas, porque el documento es CSV).
- Un modelo de lenguaje: Gemma, ChatGPT, Cohere u otro — **en este proyecto se usa Gemini** (ver sección 3).
- **OCI Compute** para el deploy.

### 1.3 Entregables obligatorios
- Repositorio publicado en **GitHub**, con:
  - Repositorio organizado (estructura clara de carpetas/archivos).
  - Historial de commits real y progresivo (no un solo commit gigante).
  - **README** bien elaborado que incluya:
    - Descripción de la arquitectura del proyecto.
    - Ejemplos de preguntas y respuestas que el agente puede resolver.
    - Instrucciones para ejecutar el proyecto.
  - Un **enlace o captura de pantalla** de la aplicación corriendo en OCI, como evidencia de que el deploy funcionó realmente.

### 1.4 Criterios de validación
El desafío se evalúa según:
- Si la solución funciona de verdad.
- Si el código está organizado.
- Si el README explica bien lo que se hizo y muestra evidencia del deploy en línea.

### 1.5 Consejos del desafío (a seguir durante el desarrollo)
- Empezar siempre por el **agente local**: que funcione en la máquina del usuario antes de pensar en el deploy. No subir a la nube algo que no funciona localmente.
- Usar **Google Colab** para prototipar si se necesita (gratuito, con Python ya configurado) — opcional, ya que aquí se trabaja directamente en la máquina local del usuario.
- **No obsesionarse con una interfaz visualmente atractiva**: el valor del proyecto está en que el agente funcione, no en la apariencia. El diseño de la sección 2 es una referencia funcional (qué campos y secciones debe tener), no un objetivo estético a perfeccionar.

---

## 2. Diseño de interfaz de referencia (ZenTrader — mockup del usuario)

El usuario adjuntó un mockup de interfaz ("ZenTrader — Trading with Intention") que sirve como **referencia funcional** de qué debe poder hacer la interfaz real (Streamlit). No es necesario replicar el estilo visual, colores ni tipografía — solo la funcionalidad y los campos que representa cada sección.

### 2.1 Barra lateral de navegación
- Logo/nombre de marca ("ZenTrader") — en este proyecto será "TradeMetrics AI".
- Botón principal **"+ New Entry"** → equivale al formulario de registro de operación (sección 2.3).
- Ítems de navegación: **Journal** (vista activa/principal), **Analytics**, **Psychology**, **Portfolio**. Para el MVP del desafío, solo es indispensable **Journal** (registro + listado) y el equivalente a **Analytics** (métricas). Psychology y Portfolio son candidatos a fases futuras, no requisitos del desafío.
- Pie de barra: **Settings** y perfil de usuario (nombre + rol, ej. "Alex M. — Intentional Trader"). No es prioritario para el MVP.

### 2.2 Encabezado del dashboard
- Título "Journal Dashboard".
- Barra de búsqueda ("Search entries, tickers...") — funcionalidad opcional/futura, no requisito del desafío.
- Íconos de notificaciones y calendario — no prioritarios para el MVP.

### 2.3 Tarjetas de métricas (KPIs superiores)
Cuatro tarjetas que deben calcularse a partir de los datos reales del journal (ver `metrics.py`):
- **Win Rate**: porcentaje de operaciones ganadoras (ej. "68%"), con variación reciente (ej. "+2% this week" — opcional).
- **Total PnL**: suma de resultados de todas las operaciones (ej. "+$4,250"), con etiqueta cualitativa (ej. "Consistency maintained" — opcional, puede omitirse o generarse dinámicamente).
- **Profit Factor**: ratio de ganancias brutas sobre pérdidas brutas (ej. "1.8"), con etiqueta cualitativa (ej. "Healthy risk profile" — opcional).
- **Total Trades**: número total de operaciones registradas (ej. "42"), con período de referencia (ej. "This month").

### 2.4 Formulario "Log New Trade" (registro de nueva operación)
Campos exactos a implementar en el formulario de Streamlit:
- **Asset / Ticker**: texto libre (ej. "AAPL").
- **Direction**: selector exclusivo **Long / Short**.
- **Entry Price**: número decimal.
- **Exit Price**: número decimal.
- **Result (PnL)**: número decimal (puede calcularse automáticamente a partir de entry/exit y dirección, o ingresarse manualmente).
- **Mindset & Emotional State**: selector de una opción entre etiquetas predefinidas: **Calm, Anxious, Confident, FOMO**. Este campo alimenta el análisis agrupado por estado emocional (sección 1 de `metrics.py`).
- **Campo de reflexión** (textarea): pregunta guía "What were you feeling during this trade? Was your thesis correct? Be honest with yourself." — se guarda como texto libre en el campo `notas` del modelo de datos.
- Botón **"Save Journal Entry"**: agrega el registro al CSV/DataFrame.

### 2.5 Panel "AI Trading Assistant" (chat)
- Encabezado con estado ("Online · Mindful Mode") — decorativo, no funcional.
- Historial de conversación estilo chat: mensajes del agente (con avatar/ícono) y mensajes del usuario (alineados aparte, con su nombre/avatar).
- Comportamiento esperado del agente (referencia de tono y contenido, ver ejemplo del mockup): observar patrones recientes (ej. rachas de operaciones ganadoras) y advertir sobre riesgos de comportamiento (ej. exceso de confianza) — esto corresponde al **motor de recomendaciones** (fase 4 del proyecto).
- Campo de entrada de texto ("Reflect on your thoughts...") con botón de envío — es el input de preguntas al agente vía LangChain.

### 2.6 Tabla "Recent Entries"
Listado de operaciones recientes con columnas: **Date, Asset, Type (Long/Short), Entry/Exit, Result, Mindset**. Corresponde a mostrar el DataFrame cargado (o las últimas N filas) en la interfaz Streamlit — puede implementarse con una tabla simple, sin necesidad de replicar el estilo visual.

### 2.7 Alcance para el MVP del desafío
De todo lo anterior, es **indispensable** para cumplir el desafío:
- Formulario de registro (2.4) → equivale a la Etapa 1 (procesar/almacenar datos).
- Chat con el agente (2.5) → equivale a la Etapa 2 (agente responde preguntas).
- Tarjetas de métricas (2.3) y tabla de entradas recientes (2.6) → apoyan la Etapa 2 mostrando el resultado del análisis.
Elementos como búsqueda, notificaciones, Psychology, Portfolio y Settings **no son necesarios** para cumplir el desafío y quedan fuera del alcance salvo que el usuario pida explícitamente incluirlos.

---

## 3. Definiciones técnicas del proyecto

### 3.1 Modelo de datos (journal entry)
```
fecha, activo, direccion (long/short), precio_entrada, precio_salida, pnl, estado_emocional (Calm/Anxious/Confident/FOMO), notas
```
Fuente: CSV (`data/sample_journal.csv` para pruebas, generado con datos ficticios).

### 3.2 Métricas requeridas (`metrics.py`)
- Win rate
- PnL total
- Profit factor
- Total de operaciones
- Desempeño agrupado por estado emocional (mindset)

### 3.3 Stack tecnológico
- Python 3.11+
- Pandas (carga, validación y cálculo de métricas)
- LangChain (orquestación del agente)
- **Gemini** (`langchain-google-genai`) como LLM
- Streamlit (interfaz local)
- pytest (pruebas)
- Git / GitHub (control de versiones y entrega)
- OCI Compute (deploy final)

### 3.4 Estructura de carpetas
```
src/          data_loader.py, metrics.py, agent.py
data/         sample_journal.csv
tests/        test_metrics.py
docs/         screenshots/
app.py        interfaz Streamlit
README.md
.env            (datos sensibles reales — NUNCA se sube a git, ver 3.6)
.env.example     (plantilla comentada, sí se sube a git)
.gitignore
```

### 3.6 Manejo de datos sensibles (.env)

El proyecto usa un archivo `.env` para guardar la API key de Gemini y cualquier otro dato sensible. Reglas fijas:

- `.gitignore` debe incluir `.env` (además de `__pycache__/`, `.venv/`, `*.pyc`, etc.) desde el primer commit, antes de que exista el archivo `.env` real.
- `.env.example` se crea con el formato comentado, sin ningún valor real, y sí se versiona en git:
  ```
  # API key de Gemini — obtenla en https://aistudio.google.com/app/apikey
  GOOGLE_API_KEY=

  # (agregar aquí cualquier otro valor sensible que el proyecto necesite)
  ```
- A partir de esa plantilla, crear el archivo `.env` real (copia vacía de `.env.example`, sin valores).
- **Punto de pausa obligatorio**: una vez creados `.gitignore`, `.env.example` y `.env` (vacío), detenerse y pedir al usuario que abra `.env` y escriba manualmente el valor real de `GOOGLE_API_KEY`. No continuar con el resto del código hasta que el usuario confirme que ya lo escribió.
- Nunca leer, imprimir, loguear ni citar el contenido de `.env` en ningún momento posterior. El código puede referenciar la variable de entorno (`os.getenv("GOOGLE_API_KEY")`), pero el valor en sí nunca debe aparecer en la conversación ni en los archivos versionados.

### 3.5 Convenciones de código
- Type hints en todas las funciones.
- Docstrings breves explicando propósito, parámetros y retorno.
- Funciones puras y testeables en `src/`; `app.py` solo orquesta la interfaz, sin lógica de negocio.
- Commits en formato `tipo: descripción` (`feat`, `fix`, `docs`, `chore`, `test`), uno por fase completada, nunca un commit único al final.

---

## 4. Fases del proyecto — acciones explícitas

Cada fase lista las acciones a ejecutar **de forma autónoma y en secuencia**, sin pausar entre ellas. Solo hay pausa obligatoria donde se indica explícitamente ("PAUSA"). Al terminar todas las acciones de una fase, marcarla como completa y pedir **una sola** confirmación breve para pasar a la siguiente.

### Fase 0 — Estructura inicial
- [ ] Crear carpetas `src/`, `data/`, `tests/`, `docs/screenshots/`.
- [ ] Crear `.gitignore` (`.env`, `__pycache__/`, `.venv/`, `*.pyc`, `.streamlit/`).
- [ ] Crear `.env.example` con el formato de la sección 3.6.
- [ ] Crear `.env` vacío a partir de esa plantilla.
- [ ] **PAUSA:** pedir al usuario que escriba `GOOGLE_API_KEY` en `.env` y confirme.
- [ ] Crear entorno virtual e instalar `pandas`, `langchain`, `langchain-google-genai`, `streamlit`, `python-dotenv`, `pytest` en `requirements.txt`.
- [ ] Crear `README.md` con título y objetivo del proyecto.
- [ ] `git init`, commit `chore: estructura inicial del proyecto TradeMetrics AI`, push.

### Fase 1 — Carga de datos (Etapa 1 del desafío)
- [ ] Crear `src/data_loader.py`: esquema del journal (sección 3.1) + función de carga/validación con Pandas.
- [ ] Generar `data/sample_journal.csv` con 15-20 operaciones ficticias.
- [ ] Ejecutar el módulo para verificar que carga sin errores.
- [ ] Commit `feat: carga y validación de datos del journal desde CSV`, push.

### Fase 2 — Métricas
- [ ] Crear `src/metrics.py`: win rate, PnL total, profit factor, total de operaciones, agrupación por mindset (sección 3.2).
- [ ] Crear `tests/test_metrics.py` con pytest.
- [ ] Ejecutar pytest y confirmar que todo pasa.
- [ ] Commit `feat: cálculo de métricas de rendimiento`, push.

### Fase 3 — Agente conversacional (Etapa 2 del desafío)
- [ ] Crear `src/agent.py`: agente LangChain + Gemini, con las funciones de `metrics.py` como tools.
- [ ] Cargar `GOOGLE_API_KEY` desde `.env` vía `python-dotenv` (sin exponer su valor).
- [ ] Probar por consola con 2-3 preguntas de ejemplo sobre `sample_journal.csv`.
- [ ] Commit `feat: agente LangChain para consultas en lenguaje natural`, push.

### Fase 4 — Motor de recomendaciones
- [ ] Extender `src/agent.py` con detección de patrones (rachas, mindset asociado a pérdidas) y prompt de sistema para recomendaciones.
- [ ] Probar con una pregunta tipo "¿algún consejo para mi próxima operación?".
- [ ] Commit `feat: motor de recomendaciones basado en patrones del journal`, push.

### Fase 5 — Interfaz Streamlit
- [ ] Crear `app.py`: tarjetas de métricas (2.3), formulario "Log New Trade" (2.4), chat del agente (2.5), tabla de entradas recientes (2.6).
- [ ] Ejecutar `streamlit run app.py` y verificar que carga sin errores.
- [ ] Commit `feat: interfaz Streamlit para registro y análisis`, push.

### Fase 6 — Pruebas end-to-end
- [ ] Ejecutar manualmente: cargar CSV → ver métricas → preguntar al agente → registrar operación nueva → volver a preguntar.
- [ ] Guardar capturas en `docs/screenshots/`.
- [ ] Commit `docs: capturas de pruebas locales end-to-end`, push.

### Fase 7 — README final
- [ ] Completar `README.md`: arquitectura, ejemplos reales de preguntas/respuestas, instrucciones de instalación y ejecución (incluyendo cómo configurar `.env` a partir de `.env.example`).
- [ ] Commit `docs: README con arquitectura, ejemplos e instrucciones de uso`, push.

### Fase 8 — Deploy en OCI (Etapa 3 del desafío)
- [ ] **PAUSA:** confirmar con el usuario antes de crear/configurar recursos reales en OCI (implica credenciales de nube y posible costo).
- [ ] Guiar la creación de la instancia OCI Compute, apertura de puertos, instalación de dependencias y ejecución persistente.
- [ ] Verificar que la app es accesible públicamente.
- [ ] Guardar captura/enlace en `docs/screenshots/` y en el README.
- [ ] Commit `docs: enlace y captura del deploy funcionando en OCI`, push.

---

## 5. Alcance, permisos y forma de trabajo (obligatorio)

### 5.1 Alcance
- Trabajo limitado **exclusivamente** a la carpeta de este proyecto. Nunca tocar archivos, configuración o repositorios fuera de ella.
- Nunca instalar paquetes globales ni modificar configuración del sistema.
- El contenido de `.env` nunca se lee, imprime ni cita (ver 3.6).

### 5.2 Ejecución dentro de una fase — trabajar al máximo, preguntar lo mínimo
- Todas las acciones listadas en el checklist de una fase (sección 4) están **pre-aprobadas**: se ejecutan en secuencia sin pausar a pedir confirmación una por una (crear/editar archivos, instalar dependencias, ejecutar código, `git add`/`commit`/`push`).
- Solo hay dos motivos válidos para pausar en medio de una fase:
  1. Un punto marcado explícitamente como **PAUSA** en la sección 4 (ej. escribir la API key, confirmar antes del deploy real en OCI).
  2. Una decisión ambigua no cubierta por este documento (ej. un dato del modelo que falta, una elección técnica no definida).
- Fuera de esos dos casos, no interrumpir el trabajo para pedir permiso.

### 5.3 Comunicación — sin comentarios innecesarios
- No narrar cada acción completada ni explicar de más. Al terminar una fase, reportar en una sola línea qué se completó y pedir confirmación para avanzar a la siguiente (ej. "Fase 2 completa, tests en verde. ¿Continúo con la Fase 3?").
- No iniciar conversación salvo que se trate de: un punto de PAUSA, una decisión ambigua, un error que impide continuar, o el usuario pidiendo un cambio.
- No avanzar a la siguiente fase sin la confirmación del usuario.
