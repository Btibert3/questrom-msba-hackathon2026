# MSBA Hackathon 2026 — LLM Demo Stack

A cloneable demo showing how to wire together four free-tier cloud tools into a working AI data pipeline — built for a 30-minute lightning session.

---

## The Tools

**[Modal](https://modal.com)** — Serverless compute that lets you run Python functions in the cloud, including on GPUs, with no infrastructure to manage. You write a normal Python file, decorate your class, and `modal deploy` ships it. Cold starts spin up a container on demand; you only pay for actual runtime.

**[MotherDuck](https://motherduck.com)** — A cloud-hosted version of DuckDB. DuckDB is an in-process analytical database — think SQLite but fast for columnar queries. MotherDuck adds persistence and sharing on top, so your tables live in the cloud and can be queried from anywhere with a token.

**[Prefect](https://prefect.io)** — A workflow orchestration framework for Python. You decorate functions as `@task` and `@flow`, and Prefect handles scheduling, retries, logging, and a UI to monitor runs. No YAML, just Python.

**[LangSmith](https://smith.langchain.com)** — Observability for LLM applications. When you use LangChain, LangSmith automatically captures every prompt, response, token count, and latency — giving you a trace you can inspect in the browser without adding logging code.

---

## How We Use Them

| Tool | Role in this demo |
|------|-------------------|
| Modal | Hosts a SmolLM2-1.7B model on a T4 GPU as an OpenAI-compatible HTTP endpoint |
| MotherDuck | Stores the tips dataset loaded by our pipeline flow; queried by the LangChain flow |
| Prefect | Orchestrates three flows: data ingestion, LLM call, and LangChain chain |
| LangSmith | Traces the LangChain flow so you can inspect prompts and responses in the dashboard |

---

## Quick Start

### 1. Install uv

[uv](https://docs.astral.sh/uv/) is a fast Python package and project manager. Install it once — see the [official install instructions](https://docs.astral.sh/uv/getting-started/installation/) for your OS (Mac, Linux, and Windows are all supported).

### 2. Clone, install dependencies, and configure

```bash
git clone https://github.com/your-org/questrom-msba-hackathon2026.git
cd questrom-msba-hackathon2026
uv sync                  # creates .venv and installs all dependencies
```

Copy `.env.example` to `.env` and fill in your keys (see [docs/setup.md](docs/setup.md)).

### 3. Deploy the Modal LLM endpoint

```bash
uv run modal setup          # one-time browser login
uv run modal deploy modal/serve.py
# copy the printed /chat URL into MODAL_CHAT_URL in .env
```

### 3. Start everything locally

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| Prefect UI | http://localhost:4201 |
| Streamlit chat | http://localhost:8502 |

### 4. Run the flows

In the Prefect UI (http://localhost:4201), trigger each flow manually, or run them directly:

```bash
# inside the prefect-worker container or with your local venv
python workflows/pipeline_flow.py    # loads tips data → MotherDuck
python workflows/llm_flow.py         # calls Modal endpoint
python workflows/langchain_flow.py   # LangChain chain + LangSmith trace
```

---

## Repo Layout

```
├── modal/
│   └── serve.py          # Modal LLM app (SmolLM2-1.7B on T4 GPU)
├── workflows/
│   ├── pipeline_flow.py  # fetch tips CSV → MotherDuck
│   ├── llm_flow.py       # single-prompt call to Modal
│   └── langchain_flow.py # LangChain chain with LangSmith tracing
├── app/
│   └── app.py            # Streamlit multi-turn chat UI
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Docs

- [Account & key setup](docs/setup.md)
- [Flow walkthroughs](docs/workflows.md)


## Colab Flow

-[Google Colab Prototyping](https://colab.research.google.com/drive/1cNZA_oK1C0n55RVnj1AMDOevWXKLyn3P?usp=sharing)