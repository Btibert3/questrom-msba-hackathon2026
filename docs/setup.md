# Account & Key Setup

You need four accounts. All have free tiers sufficient for this demo.

---

## Modal

1. Sign up at https://modal.com
2. Run `uv run modal setup` — opens a browser for one-time auth (`modal` is already in the project dependencies)
4. After deploying `modal/serve.py`, copy the printed `/chat` endpoint URL

No Modal credentials are needed in `.env`. Authentication is handled by `modal setup` and stored locally by the Modal CLI.

`.env` key:
```
MODAL_CHAT_URL=https://<your-modal-username>--hackathon-llm-llm-chat.modal.run
```

---

## MotherDuck

1. Sign up at https://motherduck.com
2. Go to Settings → Access Tokens → Create token
3. Copy the token into `.env`

Before running `pipeline_flow.py`, create the database once:

```python
import duckdb
con = duckdb.connect("md:?motherduck_token=<your_token>")
con.execute("CREATE DATABASE IF NOT EXISTS hackathon")
con.close()
```

Or just run `pipeline_flow.py` — it calls `CREATE DATABASE IF NOT EXISTS` automatically.

`.env` key:
```
MOTHERDUCK_TOKEN=<your token>
```

---

## LangSmith

1. Sign up at https://smith.langchain.com
2. Go to Settings → API Keys → Create API Key (Personal)
3. Create a project named `hackathon2026` (or any name — set it in `.env`)

`.env` keys:
```
LANGSMITH_API_KEY=<your key>
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=hackathon2026
```

---

## Prefect

No account needed — Prefect runs entirely inside Docker via `docker compose up`. The UI is available at http://localhost:4201.

If you want cloud-hosted Prefect instead, sign up at https://prefect.io and follow their cloud quickstart — but for this demo, local is fine.
