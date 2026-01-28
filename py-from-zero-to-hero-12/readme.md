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

![alt text](image.png)

## JSON output

```json
{
  "IMG_9294.png": {
    "ocr_text": "ria do Fran\n\nFarmacia Fura\npir. lec:\navenida Bombe 110\n\n‘eI -352 OV )\nCédigo Postal: 3880-94 i\nContribuinte: 506990826 A\n\nTelefone: 956591161 as\n(Chanada para a rede f1x@ nacional)\n\nEmail: ‘armaciadofuradourcégma || COM\n\nxjhS-Processado por Prograila\nCertificado n? 1665/A1\n\nFactura FR 1FR1/92283\n\nData: 2025-12-08 11:21\n\n(132143) (SV)\n\n| Sees sS see\n\nDesignacao\npyp......",
    "fields": [
      {
        "field": "store_name",
        "value": "Farmacia Fura"
      },
      {
        "field": "street",
        "value": "avenida Bombe 110"
      },
      {
        "field": "postal_code",
        "value": "3880-94 i"
      },
      {
        "field": "owner",
        "value": "506990826"
      },
      {
        "field": "phone_number",
        "value": "956591161"
      },
      {
        "field": "email_address",
        "value": "armaciadofuradourcégma || COM"
      },
      {
        "field": "processed_by",
        "value": "Prograila"
      },
      {
        "field": "certificate_number",
        "value": "1665/A1"
      },
      ....
    ]
  },
  "IMG_9295.png": {
    "ocr_text": "CNT Ovar\nsMEPCADOS 5.A.\nMODE TNENTE HIPERMERCADOS | A\nRUA JOAG, MEARE, N 505 4464-503 SENHOR\n\nHORA 475\n% Registad y sob n 502011\nNe P1004 147510, 9: 40% 627.000, 001EUR\nProdutor En. proi102979; EEE PT000291;\nOL PTOSOD282. pA PrOB000504; P.....",
    "fields": [
      {
        "field": "address",
        "value": "Rua Joago, Meare, nº 505, 4464-503 Senhor"
      },
      {
        "field": "store_name",
        "value": "Hipermercados TNENTE HIPERMERCADOS A"
      },
      {
        "field": "issue_date",
        "value": "2026-01-28T10:30"
      },
      .......
      
```

# Challenge Overview: Extracting Objects from Images
In this challenge, we are going to build a vision-powered pipeline that scans a folder of images and automatically answers two key questions for each one:
What objects are present in the image?
What is this image  about? 
To do this, we’ll combine a local vision LLM (llava:7b running on Ollama) with a small amount of Python glue code that:
Loads each image from the images-to-extract folder
Encodes it as Base64 and sends it to the Ollama /api/chat endpoint
Asks the model (via a carefully crafted prompt) to return only valid JSON in a strict format:
{
  "objects": ["object1", "object2", "..."],
  "summary": "short sentence describing what this image is about"
}

This challenge is about more than just calling a model once: it’s about designing a batch-friendly image analysis that:
Handles noisy model outputs (extra text, code fences, etc.)
Enforces a predictable JSON schema
Can be reused in future steps (e.g., storing results in a database, building a UI, or combining with OCR for text-heavy images)

## Why llava model?
Unlike pure OCR or pure LLM models, LLaVA is trained to understand scenes and answer questions like:
“What objects do you see?”
“What is happening in the image?”
“Is this a kitchen or a workshop?”
“Does this look dangerous?”
“What style is this painting?”
“Is the car damaged?”
So instead of just outputting text, it provides semantic understanding, which is crucial for tasks like:
Automated labeling
Vision QA
Robotics
Safety monitoring
Dataset annotation
RAG on images

## Running the second app objects.py
Before running the second app, we need to optimize our ollama container and also pull another image model named `llava:7b`

Run Docker Ollama (port 11435):
```bash
docker run -d --name ollama \
  -p 11435:11434 \
  --network=backend-bridge-network \
  -v ollama:/root/.ollama \
  --cpus="4.0" \
  --memory="8g" \
  -e OLLAMA_NUM_PARALLEL=1 \
  -e OLLAMA_NUM_THREADS=4 \
  ollama/ollama
```

Pull the `llava:7b` model:
```bash
docker exec -it ollama bash
ollama pull llava:7b
```

root@c31b611ee2b5:/# ollama pull llava
pulling manifest 
pulling 170370233dd5: 100% ▕████████████████████████████████████████████████████████████████████████████████████████████████▏ 4.1 GB                         
pulling 72d6f08a42f6: 100% ▕████████████████████████████████████████████████████████████████████████████████████████████████▏ 624 MB                         
pulling 43070e2d4e53: 100% ▕████████████████████████████████████████████████████████████████████████████████████████████████▏  11 KB                         
pulling c43332387573: 100% ▕████████████████████████████████████████████████████████████████████████████████████████████████▏   67 B                         
pulling ed11eda7790d: 100% ▕████████████████████████████████████████████████████████████████████████████████████████████████▏   30 B                         
pulling 7c658f9561e5: 100% ▕████████████████████████████████████████████████████████████████████████████████████████████████▏  564 B                         
verifying sha256 digest 
writing manifest 
success 

```bash
docker exec -it ollama bash
ollama list
```

The output must contains `llava:7b` model

```bash
NAME               ID              SIZE      MODIFIED     
llava:7b           8dd30f6b0cb1    4.7 GB    17 hours ago  
```

Lets confirm ollama is ready to play using `curl http://localhost:11435/api/tags`

```bash
{"models":[{"name":"llava:latest","model":"llava:latest","modified_at":"2026-01-27T15:59:45.933695009Z","size":4733363377,"digest":"8dd30f6b0cb19f555f2c7a7ebda861449ea2cc76bf1f44e262931f45fc81d081","details":{"parent_model":"","format":"gguf","family":"llama","families":["llama","clip"],"parameter_size":"7B","quantization_level":"Q4_0"}},{"name":"llama3.2:latest","model":"llama3.2:latest","modified_at":"2026-01-20T14:57:16.960827012Z","size":2019393189,"digest":"a80c4f17acd55265feec403c7aef86be0c25983ab279d83f3bcd3abbcb5b8b72","details":{"parent_model":"","format":"gguf","family":"llama","families":["llama"],"parameter_size":"3.2B","quantization_level":"Q4_K_M"}}]}%                               
```

Ok, no more delays, running the app

```bash
cd py-from-zero-to-hero-12
python3.11 -m venv challenge
source challenge/bin/activate
pip install -r ./requirements.txt
python3.11 ./src/objects.py
```

The output should be:

```bash
python3.11 src/objects.py
Found 5 image(s) in /Users/renatomatos/Desktop/projects/python-adventure/py-from-zero-to-hero-12/images-to-extract

Reading image (1/5): cr7.jpeg....
      Objects: ['man in suit holding a trophy', 'award stage']
      Summary: A man in a tuxedo holds a golden ball on a stage

Reading image (2/5): marvel.png....
      Objects: ['Avengers', 'Captain Marvel', 'Spider-Man', 'Iron Man', 'Thor', 'Hulk', 'Black Panther', 'Dr. Strange', 'Wonder Woman', 'Star-Lord', 'Groot', 'Rocket Raccoon']
      Summary: A promotional image featuring a group of Marvel superheroes.

Reading image (3/5): minions.jpg....
      Objects: ['Minions', 'costumes']
      Summary: A group of minions dressed in costumes.

Reading image (4/5): store.jpeg....
      Objects: ['person', 'wine bottles']
      Summary: A person holding wine bottles in front of a shop

Reading image (5/5): work.jpeg....
      Objects: ['person wearing headphones and glasses over eyes, office setting with desk and monitor']
      Summary: A person with fake eyes sitting at a desk in an office setting.

Done.
```
