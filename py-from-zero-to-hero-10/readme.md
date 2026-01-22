## Overview
This folder showcases the same shopping-cart tool set from folder 08, now wired
into the Microsoft Agent Framework. Instead of manual loop control, the agent
runtime handles tool execution and turn management.

Key differences vs folders 08, 09 and 10:
- 08: single agent + manual tool loop (AutoGen tool-use pattern).
- 09: multi-agent GroupChat orchestration with AutoGen.
- 10: Microsoft Agent Framework ChatAgent with built-in run loop.

## What this example does
The script simulates a small ecommerce system with:
- in-memory product catalog, payment options, delivery locations
- cart management with validation
- checkout with payment and country restrictions (Portugal only)

The tool methods are reused from folder 08 via `src/shopping_tools.py`.

## Why Microsoft Agent Framework here
Pros of the framework approach in this example:
- no custom loop control: `agent.run()` handles tool calls and responses
- simpler orchestration for a single-agent workflow
- smaller dependency set (no AutoGen packages required)

## Agent setup
Defined in `src/ms_agent_sdk.py`:
- `ChatAgent` named `ShoppingAssistant`
- `OpenAIChatClient` pointing to Ollama (`http://localhost:11435/v1`)
- tools registered from `ShoppingTools` (the same one into the folder 08)

## Tools available to the agent
- `search_products(query, country)` -> available products
- `get_payment_options(country)` -> available payment methods
- `get_delivery_locations(country)` -> delivery cities (PT only)
- `add_to_cart(product_id, quantity, country, cart_id)`
- `get_cart(cart_id)`
- `checkout(cart_id, payment_method, delivery_city, delivery_country)`

## Requirements
Python 3.11:
```bash
brew install python@3.11
python3.11 --version
```

Building the ENV and installing dependencies:
```bash
cd py-from-zero-to-hero-10
python3.11 -m venv venv
source venv/bin/activate
pip install -r ./requirements.txt
```

Look at here :)

`requirements.txt` only includes:
```text
agent-framework --pre
```

## Run
```bash
python3.11 src/ms_agent_sdk.py
```

## Ollama (recommended local LLM)
The script expects a local OpenAI-compatible endpoint at `http://localhost:11435/v1`
configured for model `llama3.2`.

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

Pull the `llama3.2` model:
```bash
docker exec -it ollama bash
ollama pull llama3.2
```

Confirm the model was pulled:
```bash
docker exec -it ollama bash
ollama list
```

Expected list:
```text
NAME               ID              SIZE      MODIFIED
llama3.2:latest    a80c4f17acd5    2.0 GB    6 minutes ago
```

## Sample output
```text
{"name": "get_cart", "parameters": null}

{"name": "checkout", "parameters": {"cart_id": null, "payment_method": "PayPal", "delivery_city": "", "delivery_country": "PT"}}Here is your cart:

* Pastel de Nata Box (12 units) - 12.50
* Port Wine (Douro DOC) - 19.99

You can proceed to checkout with PayPal.
```
