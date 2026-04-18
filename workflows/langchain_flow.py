import os
from dotenv import load_dotenv

load_dotenv()

import httpx
import duckdb
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.prompts import ChatPromptTemplate
from prefect import flow, task
from typing import Any


class ModalChatModel(BaseChatModel):
    endpoint_url: str

    @property
    def _llm_type(self) -> str:
        return "modal-smollm2"

    def _generate(self, messages: list[BaseMessage], stop=None, **kwargs: Any) -> ChatResult:
        payload = {"messages": [{"role": m.type if m.type != "human" else "user", "content": m.content} for m in messages]}
        response = httpx.post(self.endpoint_url, json=payload, timeout=120)
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"]
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=text))])


@task
def fetch_pitch_summary() -> str:
    token = os.environ["MOTHERDUCK_TOKEN"]
    con = duckdb.connect(f"md:?motherduck_token={token}")
    con.execute("USE hackathon")
    df = con.execute("""
        SELECT pitcher_name, pitch_type, COUNT(*) AS pitches,
               ROUND(AVG(start_speed), 1) AS avg_speed,
               SUM(CASE WHEN description LIKE '%Strike%' THEN 1 ELSE 0 END) AS strikes
        FROM pitches
        GROUP BY pitcher_name, pitch_type
        ORDER BY pitches DESC
        LIMIT 10
    """).df()
    con.close()
    return df.to_string(index=False)


@task
def run_chain(context: str) -> str:
    llm = ModalChatModel(endpoint_url=os.environ["MODAL_CHAT_URL"])
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a data analyst."),
        ("human", "Here is a summary of yesterday's MLB pitch data:\n\n{context}\n\nIn 2-3 sentences, what is the most interesting insight from this data?"),
    ])
    chain = prompt | llm
    result = chain.invoke({"context": context})
    print(f"Insight: {result.content}")
    return result.content


@flow(name="langchain-flow")
def langchain_flow():
    context = fetch_pitch_summary()
    run_chain(context)


if __name__ == "__main__":
    langchain_flow()
