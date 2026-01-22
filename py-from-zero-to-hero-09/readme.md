## Overview
This folder demonstrates a real multi-agent shopping cart flow using Autogen's
GroupChat. Multiple specialized agents collaborate in a shared conversation,
and a UserProxy agent executes tools on their behalf.

Key differences vs folder 08:
- 08: single agent uses tools; other agents are declared but do not speak.
- 09: multiple agents speak, share context, and a GroupChatManager routes turns.

## What this example does
The script simulates a small ecommerce system with:
- in-memory product catalog, payment options, delivery locations
- cart management with validation
- checkout with payment and country restrictions (Portugal only)

## Agents and roles
Defined in `src/shopping-cart-multi-agent.py`:
- `admin` (UserProxyAgent): executes tools and handles termination
- `shopping_assistant`: gathers requirements and coordinates agents
- `catalog_agent`: searches products and checks availability by country
- `checkout_agent`: manages cart and performs checkout

All agents share the same conversation history.

## Tools available to agents
Registered for LLM planning (all assistants) and execution (admin):
- `search_products(query, country)` -> available products
- `get_payment_options(country)` -> available payment methods
- `get_delivery_locations(country)` -> delivery cities (PT only)
- `add_to_cart(product_id, quantity, country, cart_id)`
- `get_cart(cart_id)`
- `checkout(cart_id, payment_method, delivery_city, delivery_country)`

## Data model (in-memory)
The catalog and options are mocked in the script:
- Products: P001..P004 (PT/ES availability rules)
- Payment methods: paypal, credit_card, debit_card, mbway
- Delivery locations: Lisboa, Porto, Coimbra, Faro (PT only)

## Flow summary
1) `shopping_assistant` reads user intent and asks for missing details.
2) `catalog_agent` validates product availability using `search_products`.
3) `checkout_agent` adds items, shows cart, and runs `checkout`.
4) `admin` executes tool calls and returns results to the group chat.
5) Conversation ends when a termination message is detected.

`GroupChat` is configured with `max_round=10`.

## Requirements
Python 3.11:
```bash
brew install python@3.11
python3.11 --version
```

## Setup
Create a virtual environment named `venv`:
```bash
cd py-from-zero-to-hero-09
python3.11 -m venv venv
```

Activate it:
```bash
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r ./requirements.txt
```

## Run
```bash
python3.11 src/shopping-cart-multi-agent.py
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
Next speaker: shopping_assistant
... tool calls ...
Next speaker: admin
... tool results ...
shopping_assistant:
Summary:
* We were unable to find the requested products in our catalog.
* The delivery locations for Lisbon, Portugal are:
  - Lisboa
  - Porto
  - Coimbra
  - Faro
* To complete your order, please select a valid cart_id and delivery_city.
TERMINATE
```
