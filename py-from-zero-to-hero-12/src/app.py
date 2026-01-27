import asyncio
import glob
import json
import os
import re
from typing import Any, Dict, List
from pathlib import Path

from PIL import Image
import pytesseract

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient

# ----------------------------
# CONFIGURATION
# ----------------------------

IMAGES_FOLDER = "images"

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11435/v1")
OLLAMA_MODEL_ID = os.getenv("OLLAMA_MODEL_ID", "llama3.2")

# this big instruction block \0/ exists to make the model behave like a
# deterministic extraction engine instead of a creative writer, so we can
# reliably plug its output into our Python code without surprises:
# - define a strict contract for the output
# - reduce ambiguity for the model
# - enforce a consistent schema
# - protect the pipeline from JSON errors
AGENT_INSTRUCTIONS = """
You are an AI specialized in extracting structured data from real-world documents.

You will receive OCR text from an image of one of the following document types:
- Supermarket invoice (Brazilian / Portuguese or English)
- Gas station receipt
- Medical consultation invoice / receipt

Your goal:
- Identify and extract EVERY relevant field and value present in the text.
- Return ONLY a JSON array. No explanations, no comments, no extra text.

Output format (example):
[
  { "field": "store_name", "value": "Supermarket XPTO" },
  { "field": "contribuinte", "value": "506990826" },
  { "field": "issue_date", "value": "2026-01-28" },
  { "field": "total_amount", "value": "34.40" }
]

Rules:
- Use snake_case for field names.
- Include as many fields as possible (store, address, CNPJ/NIF, dates, total, items, payment method, etc.).
- If a field exists but the value is unclear, set "value" to "" (empty string).
- IMPORTANT: The response MUST be valid JSON. Do NOT wrap it in markdown fences.
- No trailing commas.
- Do NOT add any natural language outside the JSON.
- Do not output nested JSON objects or arrays. Flatten all information into { "field": "...", "value": "..." } form. 
- Each piece of extracted information must have exactly one field and one value.
- If the invoice has multiple line items, output them as:
{ "field": "item_1", "value": "Chocolate Pintarolas 8x220" }
{ "field": "item_2", "value": "Mochas (poupança)" }
"""

# ----------------------------
# AGENT SETUP (Microsoft Agent Framework + Ollama)
# ----------------------------

def create_extraction_agent():
    """
    Creates a Microsoft Agent Framework ChatAgent that talks to Ollama via
    OpenAI-compatible API using OpenAIChatClient.
    """
    chat_client = OpenAIChatClient(
        model_id=OLLAMA_MODEL_ID,
        api_key="ollama",  # a minor reminder.. for ollama we can use an empty string            
        base_url=OLLAMA_BASE_URL,    
    )

    agent = ChatAgent(
        chat_client=chat_client,
        name="DocumentFieldExtractor",
        instructions=AGENT_INSTRUCTIONS,
    )

    return agent


# ----------------------------
# OCR HELPERS
# ----------------------------

def ocr_image_to_text(image_path: str) -> str:
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang="por+eng")
    return text

# Thanks stackoverflow \0/
def extract_field_value_pairs_fallback(content: str) -> List[Dict[str, Any]]:
    """
    Fallback parser when JSON is invalid:
    Extracts all occurrences of {"field": "...", "value": "..."} from the text
    using a regex, even if the overall JSON is broken.
    """
    pattern = r'\{\s*"field"\s*:\s*"([^"]*)"\s*,\s*"value"\s*:\s*"([^"]*)"\s*[\}\]]'
    matches = re.findall(pattern, content)

    return [
        {"field": field.strip(), "value": value.strip()}
        for field, value in matches
    ]

# ----------------------------
# LLM CALL + JSON PARSING
# ----------------------------

async def extract_fields_from_text(agent, ocr_text: str) -> List[Dict[str, Any]]:
    user_prompt = f"""
You will receive the OCR text of a document.
Extract EVERY relevant field and value and output ONLY the JSON array.

OCR TEXT:
{ocr_text}
"""

    result = await agent.run(user_prompt)

    content = getattr(result, "text", str(result)).strip()

    # Remove possible fences ```json ... ```
    if content.startswith("```"):
        content = content.strip("`")
        if content.lower().startswith("json"):
            content = content[4:].strip()

    # 1ª Try to parse the JSON with a fallback
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        # fixing possible missed []
        s = content.strip()
        if s.startswith("[") and not s.rstrip().endswith("]"):
            s = s.rstrip() + "]"
            try:
                parsed = json.loads(s)
            except Exception:
                parsed = None
        else:
            parsed = None

        # maybe a second shot using regex :(
        if parsed is None:
            fallback = extract_field_value_pairs_fallback(content)
            if not fallback:
                raise ValueError(f"Model returned invalid JSON:\n{content}")
            return fallback

    # at the end we need an array to build our dictionary
    if isinstance(parsed, dict):
        parsed = [parsed]
    if not isinstance(parsed, list):
        raise ValueError("Model did not return a JSON array.")

    return parsed

# ----------------------------
# MAIN PIPELINE
# ----------------------------

async def process_all_images():
    agent = create_extraction_agent()

    # Find all images in the images folder
    patterns = ("*.png", "*.jpg", "*.jpeg", "*.tif", "*.tiff", "*.bmp")
    image_paths: List[str] = []
    for pattern in patterns:
        image_paths.extend(glob.glob(os.path.join(IMAGES_FOLDER, pattern)))

    if not image_paths:
        print(f"No images found in folder '{IMAGES_FOLDER}'.")
        return
    
    # build the output path where output.json file is going to be placed
    base_dir = Path(__file__).resolve().parents[1]
    output_path = base_dir / "src" / "output.json"

    # prepares the output array
    results: Dict[str, Any] = {}

    for image_path in image_paths:
        filename = os.path.basename(image_path)
        print(f"Processing: {image_path} ...")
        ocr_text = ocr_image_to_text(image_path)

        try:
            fields = await extract_fields_from_text(agent, ocr_text)
            # fields is already a list of { "field": ..., "value": ... } along with the extracted OCR content
            results[filename] = {
                "ocr_text": ocr_text,
                "fields": fields
            }
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            results[filename] = {"error": str(e)}

    # Write JSON with proper UTF-8 characters and the new fields
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(
            results,
            handle,
            indent=2,
            ensure_ascii=False,
        )

    print(f"DONE! Output written to: {output_path}")


if __name__ == "__main__":
    asyncio.run(process_all_images())
