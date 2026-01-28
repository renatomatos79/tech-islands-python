from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import httpx

app = FastAPI()


class AnalyzeRequest(BaseModel):
    task: str  # "generate_tests" | "add_header_comments" | "fix_errors"
    language: str | None = None
    code: str


class AnalyzeResponse(BaseModel):
    updated_code: str
    notes: str | None = None


@app.get("/ping")
async def ping():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    if req.task not in {"generate_tests", "add_header_comments", "fix_errors"}:
        raise HTTPException(status_code=400, detail="Invalid task")

    prompt = build_prompt(req)
    updated_code = await call_ollama(prompt, req.code)

    return AnalyzeResponse(
        updated_code=updated_code,
        notes=f"Task '{req.task}' applied by LLM."
    )


def build_prompt(req: AnalyzeRequest) -> str:
    language = req.language or "code"

    if req.task == "generate_tests":
        return (
            f"You are a senior {language} developer.\n"
            "Given the code below, generate unit tests ONLY.\n"
            "Return ONLY the test code, no explanations.\n"
        )

    if req.task == "add_header_comments":
        return (
            f"You are a senior {language} developer.\n"
            "Add a clear function/method header comment explaining parameters, "
            "return value and side effects.\n"
            "Return the FULL updated code, no extra text.\n"
        )

    if req.task == "fix_errors":
        return (
            f"You are a senior {language} developer.\n"
            "Fix compilation/runtime errors, undefined variables, wrong loops, etc.\n"
            "Keep the style and structure; do not add new features.\n"
            "Return the FULL fixed code as plain code only.\n"
            "Do NOT include Markdown formatting or code fences.\n"

        )

    # Fallback (should not normally be used)
    return f"You are a helpful {language} assistant. Improve the code."


async def call_ollama(prompt: str, code: str) -> str:
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder")

    print(f"[OLLAMA] URL: {ollama_url}, model: {model}")  # <--- debug

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": f"{prompt}\n\n--- CODE START ---\n{code}\n--- CODE END ---",
            }
        ],
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(f"{ollama_url}/api/chat", json=payload)
        print(f"[OLLAMA] Status: {resp.status_code}")      # <--- debug
        print(f"[OLLAMA] Body: {resp.text}")               # <--- debug
        resp.raise_for_status()
        data = resp.json()
        return data["message"]["content"].strip()

