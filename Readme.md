<div align="center">
  <h1>HardiBot v3.0</h1>
  <p><b>Agente Multi-Persona con LangGraph, RAG, Scrapers y Observabilidad en Tiempo Real</b></p>
  
  ![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)
  ![Docker](https://img.shields.io/badge/Docker-Production_Ready-2496ED?logo=docker&logoColor=white)
  ![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-orange?logo=langchain&logoColor=white)
  ![Streamlit](https://img.shields.io/badge/Streamlit-Web_UI-FF4B4B?logo=streamlit&logoColor=white)
  ![Tests](https://img.shields.io/badge/Tests-41/41_passed-brightgreen)
  ![Duoc UC](https://img.shields.io/badge/Duoc_UC-Ingenier%C3%ADa_en_Inform%C3%A1tica-yellow)
</div>

---

## Arquitectura

```
 Usuario (CLI / Streamlit)
        |
        v
 HardiBotAppState (core.py)
   |-- RAG Engine (rag_engine.py) --> FAISS + CSV
   |-- LLM (GPT-4o via GitHub Models)
   |-- Tools: buscar_catalogo | buscar_web | calcular_presupuesto
   |          buscar_foto | agregar_al_carrito | ver_carrito
   |-- Persona (personas.py) --> Prompt + Catalogo especifico
   |-- ToolCaptureHandler --> Dashboard en tiempo real
   |-- Observabilidad (observability.py) --> LangSmith API
        |
        v
 Scrapers (src/scrapers/)
   |-- KnastaScraper      (knasta.cl __NEXT_DATA__)
   |-- SoloTodoScraper    (api.solotodo.com)
   |-- SyntheticGenerator (datos sinteticos en memoria)
        |
        v
 Catalogos CSV (data/*.csv)
```

## Stack Tecnologico

| Capa | Tecnologia | Descripcion |
|:-----|:-----------|:------------|
| Motor de IA | `GPT-4o` | Inferencia via GitHub Models API |
| Orquestacion | `LangGraph` | Maquina de estados con ciclo ReAct |
| Herramientas | `Function Calling` | 6 tools: RAG, web, calculadora, fotos, carrito |
| Presentacion | `Streamlit` | UI web con dashboard de transparencia |
| Observabilidad | `LangSmith` | Trazabilidad de tokens, latencia y herramientas |
| Infraestructura | `Docker` | Contenedorizacion en puerto 8501 |

---

## Guia de Despliegue

### 1. Clonar y configurar entorno

```bash
git clone https://github.com/DiVilota/Soluciones-con-IA-Eva-1.git
cd Soluciones-con-IA-Eva-1
git checkout features/summit-hardibot

cp .env.example .env
# Editar .env con tus credenciales
```

### 2. Variables de entorno requeridas

| Variable | Descripcion | Requerido |
|:---------|:------------|:----------|
| `GITHUB_TOKEN` | Token de GitHub Models | Si |
| `TAVILY_API_KEY` | API key para busqueda web Tavily | No (fallback DuckDuckGo) |
| `LANGCHAIN_API_KEY` | API key de LangSmith para trazabilidad | No |
| `LANGCHAIN_TRACING_V2` | Habilitar trazabilidad (`true`) | No |
| `LANGCHAIN_PROJECT` | Nombre del proyecto en LangSmith | No |
| `OPENAI_BASE_URL` | URL base de GitHub Models | No (default: models.inference.ai.azure.com) |
| `MODEL_NAME` | Modelo LLM (default: `gpt-4o`) | No |
| `PERSONA_ID` | Persona inicial: `hardware`, `ferreteria` o `repuestos` | No |

> **Nota:** El codigo soporta ambas convenciones de LangSmith: `LANGSMITH_*` y `LANGCHAIN_*`. Ver `.env.example`.

### 3. Docker Compose

```bash
docker-compose build --no-cache
docker-compose up
# Acceder en http://localhost:8501
```

### 4. Ejecucion local (sin Docker)

```bash
pip install -r requirements.txt
streamlit run app.py
# O CLI: python main.py
```

---

## Modulos del Proyecto

| Archivo | Proposito |
|:--------|:----------|
| `src/core.py` | Agente LangGraph, 6 tools, CarritoCompras, ToolCaptureHandler, operacion_segura (AST) |
| `src/rag_engine.py` | Motor RAG con FAISS + keyword search de 2 etapas |
| `src/personas.py` | Sistema white-label: 3 personas (hardware, ferreteria, repuestos) |
| `src/observability.py` | Dashboard LangSmith: metricas, runs, ahorro estimado |
| `src/config.py` | Acceso centralizado a variables de entorno |
| `src/crew_hardibot.py` | Demo de orquestacion multi-agente con CrewAI |
| `app.py` | Interfaz Streamlit con dashboard de transparencia |
| `main.py` | CLI interactivo con `python main.py` |

---

## Scrapers y Generacion de Catalogo

El proyecto incluye 3 scrapers para construir catalogos de productos reales y sinteticos:

| Scraper | Fuente | Datos |
|:--------|:-------|:------|
| **KnastaScraper** | knasta.cl (Next.js SSR) | Precios reales CLP de 7 categorias de hardware |
| **SoloTodoScraper** | api.solotodo.com | Precios reales de 9 categorias |
| **SyntheticCatalogGenerator** | Datos embebidos en memoria | 65+ productos pre-cargados con precios base |

### Generar catalogo

```bash
# Desde Knasta (datos reales de tiendas chilenas)
python scripts/build_catalog.py --source knasta --max 15

# Desde SoloTodo (API publica)
python scripts/build_catalog.py --source solotodo --max 15

# Hibrido: intenta Knasta > SoloTodo > Sintetico
python scripts/build_catalog.py --source hybrid --max 15

# Sintetico (offline)
python scripts/build_catalog.py --source synthetic --max 15

# Conservar catalogo existente sin sobrescribir
python scripts/build_catalog.py --source knasta --preserve
```

El catalogo se guarda en `data/catalogo_hardware.csv` y se reconstruye el indice FAISS automaticamente.

---

## Sistema White-Label Multi-Persona

HardiBot soporta 3 personas intercambiables en caliente:

| ID | Nombre | Catalogo | Rubro |
|:---|:-------|:---------|:------|
| `hardware` | HardiBot | `catalogo_hardware.csv` | Hardware de PC |
| `ferreteria` | FerriBot | `catalogo_ferreteria.csv` | Ferreteria y construccion |
| `repuestos` | AutoPartBot | `catalogo_repuestos.csv` | Repuestos automotrices |

### Cambiar persona

- **En Streamlit:** Botones en la sidebar
- **En CLI:** Escribe `/persona ferreteria`
- **Por comando:** Cambia `PERSONA_ID=ferreteria` en `.env`

### Agregar una nueva persona

1. Agregar entrada en `src/personas.py::PERSONAS` con su `id`, `prompt`, `moneda` y `catalogo`
2. Crear el CSV del catalogo en `data/`
3. Reiniciar — HardiBot carga la nueva persona automaticamente

---

## Herramientas del Agente

| Herramienta | Funcion | Fallback |
|:------------|:--------|:---------|
| `buscar_catalogo` | Busca productos en FAISS + keyword match | - |
| `buscar_web` | Busca en internet via Tavily API | DuckDuckGo |
| `calcular_presupuesto` | Evaluador matematico seguro (AST) | Rechaza codigo malicioso |
| `buscar_foto_componente` | Busca imagenes del producto | DuckDuckGo |
| `agregar_al_carrito` | Agrega items al carrito de compras | - |
| `ver_carrito` | Muestra total y detalle | - |

---

## Tests

```bash
# Todos los tests (41)
python -m pytest tests/ -v

# Por modulo
python -m pytest tests/test_core.py -v         # Operaciones, carrito, captura
python -m pytest tests/test_scrapers.py -v     # Base, knasta, synthetic
python -m pytest tests/test_rag.py -v          # FAISS, keyword search
python -m pytest tests/test_observability.py -v # Metricas LangSmith
python -m pytest tests/test_config.py -v       # Configuracion env vars
```

### Cobertura actual: 41 tests

| Suite | Tests | Que cubre |
|:------|:-----:|:----------|
| `test_core.py` | 14 | `operacion_segura` (8), `CarritoCompras` (5), `ToolCaptureHandler` (4) |
| `test_scrapers.py` | 11 | `CatalogScraper` (4), `Synthetic` (3), `Knasta` (5) |
| `test_rag.py` | 6 | `construir_indice`, `recuperar_contexto`, `recargar` |
| `test_observability.py` | 4 | Metricas, ahorro, runs invalidos |
| `test_config.py` | 2 | Model config, LangSmith config |

### Escenarios manuales

```bash
python scripts/test_scenarios.py
```

11 escenarios predefinidos para probar el agente end-to-end (cotizaciones, busquedas, carrito, cambio de persona).

---

## Estructura del Proyecto

```
.
+-- app.py                 # UI Streamlit
+-- main.py                # CLI interactivo
+-- conftest.py            # Mock HardiBotAppState para tests
+-- Dockerfile
+-- docker-compose.yml
+-- requirements.txt
+-- .env.example
+-- data/
|   +-- catalogo_hardware.csv
|   +-- catalogo_ferreteria.csv
|   +-- catalogo_repuestos.csv
+-- scripts/
|   +-- build_catalog.py       # Generador de catalogos multi-source
|   +-- test_scenarios.py      # Escenarios de prueba del agente
|   +-- generar_catalogos_demo.py
+-- src/
|   +-- core.py                # Agente, tools, carrito, app state
|   +-- rag_engine.py          # RAG con FAISS
|   +-- personas.py            # White-label personas
|   +-- observability.py       # Dashboard LangSmith
|   +-- config.py              # Acceso a env vars
|   +-- crew_hardibot.py       # Demo CrewAI
|   +-- scrapers/
|       +-- base.py            # ABC CatalogScraper
|       +-- knasta.py          # Scraper knasta.cl
|       +-- solotodo.py        # Scraper SoloTodo API
|       +-- synthetic.py       # Generador sintetico
+-- tests/
    +-- test_core.py
    +-- test_scrapers.py
    +-- test_rag.py
    +-- test_observability.py
    +-- test_config.py
```

---

## Evaluacion via LangSmith

1. Haz una consulta en Streamlit o CLI
2. Ve a tu proyecto en [smith.langchain.com](https://smith.langchain.com)
3. Revisa el Run mas reciente para ver:
   - Tokens usados y latencia
   - Herramientas invocadas con sus inputs/outputs
   - Ahorro estimado de tokens por uso de herramientas

---

Documentacion tecnica elaborada para Ingenieria de Soluciones con Inteligencia Artificial.
Integrantes: Diego Villota e Ignacio Chacon
