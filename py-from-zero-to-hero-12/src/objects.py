import base64
import json
import requests
from pathlib import Path

# https://ollama.com/library/llava:7b"
# LLaVA is a novel end-to-end trained large multimodal model that combines a vision encoder and Vicuna for general-purpose visual and language understanding. Updated to version 1.6.
OLLAMA_URL = "http://localhost:11435/api/chat"
MODEL = "llava:7b"  


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def extract_json_from_text(text: str) -> dict:
    """
    Try to extract a JSON object from the model output, even if it wraps it
    in extra text or code fences.
    """
    text = text.strip()

    # If it came as ```json ... ``` or ``` ... ```
    if text.startswith("```"):
        lines = text.splitlines()
        # drop the first line (``` or ```json)
        lines = lines[1:]
        # drop the last line if it's ```
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # Try to isolate the first {...} block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        candidate = text[start : end + 1]
    else:
        candidate = text

    return json.loads(candidate)


def analyze_image(path: Path):
    image_b64 = encode_image(str(path))

    prompt = (
        "You are a vision assistant. Analyze the image and respond ONLY with valid JSON. "
        "Do not include any markdown, explanation, comments or backticks.\n"
        "The JSON format must be exactly:\n"
        "{\n"
        '  "objects": ["object1", "object2", ...],\n'
        '  "summary": "short sentence describing what this image is about"\n'
        "}\n"
    )

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [image_b64],
            }
        ],
        "stream": False,
    }

    resp = requests.post(OLLAMA_URL, json=payload)

    if resp.status_code != 200:
        print("Ollama error:", resp.text)
        resp.raise_for_status()

    raw = resp.json()
    content = raw["message"]["content"]
    # Debug: see what the model actually sent
    # print("RAW CONTENT:\n", repr(content))

    data = extract_json_from_text(content)
    return data["objects"], data["summary"]


# get image path
base_dir = Path(__file__).resolve().parents[1]
images_dir = base_dir / "images"
image_filename = images_dir / "photo.jpeg"

if not image_filename.exists():
    raise FileNotFoundError(f"Image not found: {image_filename}")

objects, summary = analyze_image(image_filename)
print("Objects:", objects)
print("Summary:", summary)
