import modal

MODEL_ID = "HuggingFaceTB/SmolLM2-1.7B-Instruct"

image = (
    modal.Image.debian_slim()
    .pip_install("transformers", "torch", "accelerate", "fastapi[standard]")
)

app = modal.App("hackathon-llm")


@app.cls(image=image, gpu="T4")
class LLM:
    @modal.enter()
    def load(self):
        from transformers import pipeline
        self.pipe = pipeline(
            "text-generation",
            model=MODEL_ID,
            device_map="auto",
            max_new_tokens=256,
        )

    @modal.fastapi_endpoint(method="POST")
    def complete(self, request: dict) -> dict:
        prompt = request.get("prompt", "")
        messages = [{"role": "user", "content": prompt}]
        result = self.pipe(messages)
        text = result[0]["generated_text"][-1]["content"]
        print(f"Prompt: {prompt!r} → {len(text)} chars")
        return {"response": text, "model": MODEL_ID}

    @modal.fastapi_endpoint(method="POST")
    def chat(self, request: dict) -> dict:
        import time, uuid
        messages = request.get("messages", [])
        result = self.pipe(messages)
        text = result[0]["generated_text"][-1]["content"]
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": MODEL_ID,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }
