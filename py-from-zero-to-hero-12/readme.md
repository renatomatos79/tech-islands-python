# Challenge Overview: Automated Document Extraction

The goal of this challenge is to implement an automated pipeline capable of extracting structured information from real-world documents using a local LLM (via Ollama).

The pipeline must:
- Accept images as input
- Process them through OCR
- Leverage an LLM to produce a normalized JSON array containing every relevant field and value present in the document

Isn´t a sort of tasks that can simplify be done by a simple OCR library?
No, we are leverage the agent feature in order to make easier the process to indentify the fields and format the output.
OCR is being used to extract the text but the content is not well formated.. for instance this is the OCR output and for this output
we have tbis mapped JSON

## Document Types

For the challenge, consider at least three document categories:
1. Supermarket invoice
2. Gas station receipt
3. Medical consultation receipt

Each document may vary in:
- Layout
- Formatting
- Field naming
- Language
- Abbreviations
- Structure

## Input Format

The input to the system will be an image file, such as:
- `.png`
- `.jpg`
- `.jpeg`
- `.pdf` (single page)

## LLM Extraction Requirement

The LLM will receive the raw OCR text and must output a structured response formatted as:

```json
[
  { "field": "field_name", "value": "field_content" }
]
```

## Example Expected Output

A supermarket invoice might produce output such as:

```json
[
  { "field": "store_name", "value": "Supermarket XPTO" },
  { "field": "cnpj", "value": "12.345.678/0001-99" },
  { "field": "issue_date", "value": "2026-01-28" },
  { "field": "item_name_1", "value": "Rice 5kg" },
  { "field": "item_price_1", "value": "25.90" },
  { "field": "item_name_2", "value": "Beans 1kg" },
  { "field": "item_price_2", "value": "8.50" },
  { "field": "total_amount", "value": "34.40" },
  { "field": "payment_method", "value": "Credit Card" }
]
```

A gas station receipt might instead contain:

```json
[
  { "field": "station_name", "value": "PetroFuel" },
  { "field": "fuel_type", "value": "Gasoline" },
  { "field": "liters", "value": "35.20" },
  { "field": "unit_price", "value": "1.65" },
  { "field": "total_amount", "value": "58.08" },
  { "field": "issue_date", "value": "2026-01-28" }
]
```

## Success Criteria

The challenge is considered successful if:
1. All document types produce JSON arrays
2. No relevant fields are lost
3. No malformed JSON is returned
4. The system runs offline (local OCR + local LLM)
5. Output remains consistent across document variations

# Installing OS tools

```
brew install tesseract
```

# Running our APP

```
python3.11 -m venv challenge
source challenge/bin/activate
pip install -r ./requirements.txt
python3.11 ./src/phase01.py
```