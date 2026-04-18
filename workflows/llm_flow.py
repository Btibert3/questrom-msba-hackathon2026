import os
import httpx
from dotenv import load_dotenv
from prefect import flow, task

load_dotenv()


@task
def call_modal_endpoint(prompt: str) -> str:
    url = os.environ["MODAL_ENDPOINT_URL"]
    response = httpx.post(url, json={"prompt": prompt}, timeout=120)
    response.raise_for_status()
    text = response.json()["response"]
    print(f"Response: {text}")
    return text


@flow(name="llm-flow")
def llm_flow(prompt: str = "In one sentence, what is a data pipeline?"):
    call_modal_endpoint(prompt)


if __name__ == "__main__":
    llm_flow()
