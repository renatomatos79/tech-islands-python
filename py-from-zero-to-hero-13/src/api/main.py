# FastAPI framework and HTTP error handling
from fastapi import FastAPI, HTTPException 

# Data validation for request/response models
from pydantic import BaseModel

 # Access environment variables and OS info
import os

# Async HTTP client for making external requests
import httpx                                 

# Creates a FastAPI app instance
# We have more information about APIs in the folder "py-from-zero-to-hero-02"
app = FastAPI()  


# FastAPI uses Pydantic models, so we use BaseModel to:
# - Validate incoming JSON automatically
# - Convert JSON into a Python object
# - Reject invalid requests with clear errors
class AnalyzeRequest(BaseModel):
    # Defines expected input data for the /analyze endpoint
    task: str  # allowed: "generate_tests" | "add_header_comments" | "fix_errors"
    language: str | None = None  # Optional programming language
    code: str  # Code to be analyzed

class AnalyzeResponse(BaseModel):
    # Defines output data returned from /analyze
    updated_code: str
    notes: str | None = None


@app.get("/ping")
async def ping():
    # Simple health check endpoint
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    # Validates task input (raising a BadRequest for invalid task content)
    if req.task not in {"generate_tests", "add_header_comments", "fix_errors"}:
        raise HTTPException(status_code=400, detail="Invalid task")

    # Builds text instructions for the LLM
    prompt = build_prompt(req)

    # Calls the local model to transform the code
    updated_code = await call_ollama(prompt, req.code)

    # Returns updated code plus a small note
    return AnalyzeResponse(
        updated_code=updated_code,
        notes=f"Task '{req.task}' applied by LLM."
    )


def build_prompt(req: AnalyzeRequest) -> str:
    # Use provided language or default to generic word "code"
    language = req.language or "code"

    # Generates prompt text depending on the selected task
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

    # Fallback prompt (normally unused)
    return f"You are a helpful {language} assistant. Improve the code."


async def call_ollama(prompt: str, code: str) -> str:
    # Reads model settings from environment variables
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder")

    print(f"[OLLAMA] URL: {ollama_url}, model: {model}")  # Debug output

    # Request payload for the local LLM server
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": f"{prompt}\n\n--- CODE START ---\n{code}\n--- CODE END ---",
            }
        ],
        "stream": False,  # We wait for complete response instead of streaming
    }

    # Sends HTTP POST request to Ollama
    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(f"{ollama_url}/api/chat", json=payload)
        print(f"[OLLAMA] Status: {resp.status_code}")  # Debug output
        print(f"[OLLAMA] Body: {resp.text}")  # Debug output

        resp.raise_for_status()  # Throws error if request failed
        data = resp.json()  # Converts JSON to Python dict
        return data["message"]["content"].strip()  # Returns only the LLM output
