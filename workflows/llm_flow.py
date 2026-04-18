import os
import httpx
from dotenv import load_dotenv
from prefect import flow, task

load_dotenv()


@task
def call_modal_endpoint(prompt: str) -> str:
    url = os.environ["MODAL_CHAT_URL"]
    payload = {"messages": [{"role": "user", "content": prompt}]}
    response = httpx.post(url, json=payload, timeout=120)
    response.raise_for_status()
    text = response.json()["choices"][0]["message"]["content"]
    print(f"Response: {text}")
    return text


@flow(name="llm-flow")
def llm_flow(prompt: str = "In one sentence, what is a data pipeline?"):
    call_modal_endpoint(prompt)


if __name__ == "__main__":
    llm_flow()
