# Flow Walkthroughs

Each workflow is a self-contained Prefect flow in the `workflows/` directory.

---

## pipeline_flow.py — Load Data to MotherDuck

**What it does:** Fetches the classic tips dataset (244 rows) from GitHub and loads it into a MotherDuck table called `tips`.

**Tasks:**
1. `fetch_data` — reads a CSV via pandas from a public URL
2. `load_to_motherduck` — connects to MotherDuck using your token, creates the `hackathon` database if it doesn't exist, and writes the table with `CREATE OR REPLACE`

**Run it:**
```bash
python workflows/pipeline_flow.py
```

**What to look for:** Prefect UI shows two green task runs. MotherDuck UI shows `hackathon.tips` with 244 rows.

---

## llm_flow.py — Call the Modal LLM Endpoint

**What it does:** Sends a single prompt to your deployed Modal endpoint and prints the response.

**Tasks:**
1. `call_modal_endpoint` — POSTs an OpenAI-compatible `messages` payload to `MODAL_CHAT_URL` via `httpx`

**Run it:**
```bash
python workflows/llm_flow.py
```

**What to look for:** Response printed to logs. First call may take 60–90 seconds (GPU cold start). Subsequent calls are fast.

**Change the prompt:** Edit the default in `llm_flow.py`:
```python
def llm_flow(prompt: str = "In one sentence, what is a data pipeline?"):
```

---

## langchain_flow.py — LangChain Chain + LangSmith Tracing

**What it does:** Queries MotherDuck for a tipping data summary, feeds it to a LangChain chain backed by the Modal LLM, and asks for the most interesting insight. Every call is traced to LangSmith.

**Tasks:**
1. `fetch_tips_summary` — runs a GROUP BY query in MotherDuck, returns a formatted string
2. `run_chain` — builds a `ChatPromptTemplate | ModalChatModel` chain and invokes it

**`ModalChatModel`** is a minimal `BaseChatModel` subclass that wraps the Modal endpoint — no OpenAI key required.

**Run it:**
```bash
python workflows/langchain_flow.py
```

**What to look for:**
- Insight printed to logs
- LangSmith dashboard shows the full trace: prompt, model response, latency

---

## Streamlit App — app/app.py

Not a Prefect flow, but part of the demo. Runs as a Docker service.

**What it does:** Multi-turn chat UI. Each submission sends the full conversation history to the Modal endpoint, so the LLM has context across turns.

**Access it:** http://localhost:8502 (after `docker compose up`)

**To extend it:** Add a MotherDuck query button, display tips data in a table, or add a sidebar for system prompt configuration.
