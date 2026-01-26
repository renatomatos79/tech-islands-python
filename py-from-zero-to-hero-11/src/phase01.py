import asyncio
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from pypdf import PdfReader  # type: ignore
except Exception:  # pragma: no cover - fallback import
    try:
        from PyPDF2 import PdfReader  # type: ignore
    except Exception as exc:  # pragma: no cover
        PdfReader = None  # type: ignore
        _PDF_IMPORT_ERROR = exc
    else:
        _PDF_IMPORT_ERROR = None
else:
    _PDF_IMPORT_ERROR = None

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient


# -----------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------
config_list = [
    {
        "model": "llama3.2",
        "base_url": "http://localhost:11435/v1",
        "api_key": "ollama",  # not really used, but must not be empty
        "price": [0, 0],  # prompt_price_per_1k, completion_price_per_1k
    },
]

# Cooldown between requests to avoid hammering CPU / server
COOLDOWN_SECONDS = 0.5  # adjust as needed: 0.2, 0.5, 1.0, etc.

# Retry config for transient connection issues
MAX_RETRIES = 3
BASE_RETRY_DELAY = 2  # seconds


@dataclass
class CaseResult:
    district: Optional[str]
    city: Optional[str]
    year: Optional[int]
    month: Optional[int]
    occurrence: Optional[str]
    source: str
    # New fields for reliability
    Success: bool = True
    ERROR: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "district": self.district,
            "city": self.city,
            "year": self.year,
            "month": self.month,
            "occurrence": self.occurrence,
            "source": self.source,
            "Success": self.Success,
            "ERROR": self.ERROR,
        }


def _extract_text_from_pdf(path: Path) -> str:
    if PdfReader is None:
        raise RuntimeError(
            "Missing PDF parser. Install 'pypdf' (recommended) or 'PyPDF2'."
        ) from _PDF_IMPORT_ERROR

    reader = PdfReader(str(path))
    chunks: List[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            chunks.append(text)
    return "\n".join(chunks)


def _find_json_object(text: str) -> Dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def _coerce_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        digits = re.findall(r"\d+", value)
        if digits:
            return int(digits[0])
    return None


def _normalize_result(data: Dict[str, Any], source: Path) -> CaseResult:
    district = data.get("district")
    city = data.get("city")
    occurrence = data.get("occurrence")

    return CaseResult(
        district=str(district).strip() if district is not None else None,
        city=str(city).strip() if city is not None else None,
        year=_coerce_int(data.get("year")),
        month=_coerce_int(data.get("month")),
        occurrence=str(occurrence).strip() if occurrence is not None else None,
        source=str(source),
        # Success=True and ERROR=None by default (see dataclass defaults),
        # but we could set explicitly if you prefer.
    )


def _create_agent() -> ChatAgent:
    config = config_list[0]
    chat_client = OpenAIChatClient(
        model_id=config["model"],
        api_key=config["api_key"],
        base_url=config["base_url"],
    )

    instructions = (
        "You extract structured fields from police case reports. "
        "Return ONLY a JSON object with keys: district, city, year, month, occurrence. "
        "Year and month must be numbers. Use null if missing."
    )

    return ChatAgent(
        chat_client=chat_client,
        name="CaseExtractor",
        instructions=instructions,
    )


async def _extract_case(agent: ChatAgent, text: str, source: Path) -> CaseResult:
    prompt = (
        "Extract the case data from the report below. "
        "Return ONLY the JSON object.\n\n"
        f"REPORT:\n{text}"
    )
    response = await agent.run(prompt)
    data = _find_json_object(response.text)
    return _normalize_result(data, source)


async def run_pipeline() -> List[CaseResult]:
    base_dir = Path(__file__).resolve().parents[1]
    docs_dir = base_dir / "docs"
    output_path = base_dir / "src" / "output.json"

    if not docs_dir.exists():
        raise FileNotFoundError(f"Docs folder not found: {docs_dir}")

    agent = _create_agent()
    results: List[CaseResult] = []

    pdf_files = sorted(docs_dir.glob("*.pdf"))
    total = len(pdf_files)

    if total == 0:
        raise FileNotFoundError(f"No PDF files found in: {docs_dir}")

    for idx, pdf_path in enumerate(pdf_files, start=1):
        # Pretty progress feedback on one updating line
        bar = f"[{idx}/{total}]"
        sys.stdout.write(f"\r{bar} Processing: {pdf_path.name}")
        sys.stdout.flush()

        # Extract PDF text first (if this throws, we catch below)
        try:
            text = _extract_text_from_pdf(pdf_path)
        except Exception as exc:  # noqa: BLE001
            # Fatal for this file, but not for the pipeline.
            sys.stdout.write("\n")
            print(f"Error reading PDF {pdf_path.name}: {exc}")
            error_result = CaseResult(
                district=None,
                city=None,
                year=None,
                month=None,
                occurrence=None,
                source=str(pdf_path),
                Success=False,
                ERROR=str(exc),
            )
            results.append(error_result)
            # continue with next file
            continue

        # --- Retry loop for LLM call ---
        last_exc: Optional[BaseException] = None
        result: Optional[CaseResult] = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                result = await _extract_case(agent, text, pdf_path)
                last_exc = None
                break
            except Exception as exc:  # noqa: BLE001 - generic at this level
                last_exc = exc
                # move to new line so error message doesn't overwrite progress
                sys.stdout.write("\n")
                print(
                    f"Error processing {pdf_path.name} "
                    f"(attempt {attempt}/{MAX_RETRIES}): {exc}"
                )
                if attempt < MAX_RETRIES:
                    delay = BASE_RETRY_DELAY * attempt
                    print(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)

        if last_exc is not None:
            # After all retries failed, record error in JSON and continue.
            print(f"Giving up on {pdf_path.name} after {MAX_RETRIES} failed attempts.")
            error_result = CaseResult(
                district=None,
                city=None,
                year=None,
                month=None,
                occurrence=None,
                source=str(pdf_path),
                Success=False,
                ERROR=str(last_exc),
            )
            results.append(error_result)
        else:
            # Successful processing
            # result already has Success=True, ERROR=None from defaults
            results.append(result)  # type: ignore[arg-type]

        # --- Cooldown to avoid CPU / server overload ---
        if COOLDOWN_SECONDS > 0:
            await asyncio.sleep(COOLDOWN_SECONDS)

    # Final newline so the shell prompt doesn't hug the progress line
    print()

    # Write JSON with proper UTF-8 characters and the new fields
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(
            [item.to_dict() for item in results],
            handle,
            indent=2,
            ensure_ascii=False,
        )

    return results


if __name__ == "__main__":
    asyncio.run(run_pipeline())
