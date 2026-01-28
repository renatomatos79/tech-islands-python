import base64
import json
import requests
from pathlib import Path

# Ollama HTTP endpoint (your mapped port)
OLLAMA_URL = "http://localhost:11435/api/chat"
MODEL = "llava:7b"  # <-- use the exact vision model you pulled


def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def extract_json_from_text(text: str) -> dict:
    """
    Try to extract a JSON object from the model output, even if it wraps it
    in extra text or code fences.
    """
    text = text.strip()

    # Handle ```json ... ``` or ``` ... ```
    if text.startswith("```"):
        lines = text.splitlines()
        # drop first line (``` or ```json)
        lines = lines[1:]
        # drop last line if it's ```
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
        '  \"objects\": [\"object1\", \"object2\", ...],\n'
        '  \"summary\": \"short sentence describing what this image is about\"\n'
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
        print(f"Ollama error for image {path.name}: {resp.text}")
        resp.raise_for_status()

    raw = resp.json()
    content = raw["message"]["content"]
    # Debug if needed:
    # print("RAW CONTENT:\n", repr(content))

    data = extract_json_from_text(content)
    return data["objects"], data["summary"]


if __name__ == "__main__":
    # Base / images folder
    base_dir = Path(__file__).resolve().parents[1]
    images_dir = base_dir / "images-to-extract"

    if not images_dir.exists():
        raise FileNotFoundError(f"Images folder not found: {images_dir}")

    # Collect image files (jpg, jpeg, png)
    image_files = sorted(
        [
            p
            for p in images_dir.iterdir()
            if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
        ]
    )

    if not image_files:
        raise FileNotFoundError(f"No images (.jpg/.jpeg/.png) found in {images_dir}")

    total = len(image_files)
    print(f"Found {total} image(s) in {images_dir}\n")

    for idx, image_path in enumerate(image_files, start=1):
        print(f"Reading image ({idx}/{total}): {image_path.name}....")

        try:
            objects, summary = analyze_image(image_path)
        except Exception as e:
            print(f"\nOops! Error while processing {image_path.name}: {e}")
            print("Stopping execution due to error.")
            break

        print(f"      Objects: {objects}")
        print(f"      Summary: {summary}\n")

    print("Done.")
