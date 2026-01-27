# Challenge Overview: Automated Document Extraction

The goal of this challenge is to implement an automated pipeline capable of extracting structured information from real-world documents using a local LLM (via Ollama).

The pipeline must:
- Accept images as input
- Process them through OCR
- Leverage an LLM to produce a normalized JSON array containing every relevant field and value present in the document

## Isn’t It Overkill to Add an LLM If OCR Can Handle This?

A traditional OCR library will only extract raw text from the image. This library doesn’t understand the structure, semantic meaning, or intent behind the content. For example, OCR doesn’t know whether `22,04€` refers to a unit price, a tax amount, a discount, a subtotal, or the final total. It also won’t normalize field names, separate line items, infer document type, or produce machine-readable output.

In our case, we are combining two steps:
- OCR → converts the image to plain text
- Agent/LLM → interprets that text and transforms it into structured JSON fields

The agent layer is doing the heavy lifting:
- Identifying field boundaries
- Classifying information
- Normalizing field names
- Dealing with noise
- Extracting nested values (e.g., items, dates, totals)
- Outputting a predictable JSON schema

Here’s why OCR alone isn’t enough:
- OCR output is usually noisy, fragmented, or non-linear
- Invoices differ wildly between vendors
- Multiple layouts, languages, tax systems, and fonts
- Signal-to-noise is high (headers, disclaimers, footnotes, coupons, ads, legal text)
- No “field” notion (OCR just dumps characters)

For example, given this OCR result:

```text
SUPERMERCADOS A
FS AAP204/026754
Chocolate Pintarolas 8x220
€ 22,04
poupança 6%
Total € 23,36
```

A human can easily identify these fields:
- `store_name = Supermercados A`
- `invoice_number = FS AAP204/026754`
- `item_name = Chocolate Pintarolas`
- `quantity = 8x220`
- `total_amount = 23.36`
- `discount = 6%`

But OCR libraries do not do that.

Our pipeline converts this into something structured, like:

```json
{
  "store_name": "Supermercados A",
  "invoice_number": "FS AAP204/026754",
  "items": [
    {
      "product_name": "Chocolate Pintarolas",
      "quantity": "8x220",
      "unit_price": "22.04",
      "discount": "6%"
    }
  ],
  "total_amount": "23.36"
}
```

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
  { "field": "contribuinte", "value": "500997833" },
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

## Installing OS Tools

macOS:
```bash
brew install tesseract
```

Linux: 
```bash
sudo apt-get install tesseract-ocr
```


## Running the App

```bash
python3.11 -m venv challenge
source challenge/bin/activate
pip install -r ./requirements.txt
python3.11 ./src/phase01.py
```
