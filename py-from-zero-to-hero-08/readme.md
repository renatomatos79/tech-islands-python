## Overview
This small app (shopping-cart.py) demonstrates how to build a multi-agent shopping/checkout system using AutoGen with Ollama as the LLM backend. The goal is to model realistic personas (catalog discovery, checkout, shopping assistant) while simulating interactions with backend APIs such as product catalog, payment methods, logistics and order processing.

Key characteristics:
▸ Multi-Agent Role Behavior
The application defines multiple autonomous agents with specialized responsibilities, such as:
Shopping Assistant — coordinates the entire buying flow
Catalog Agent — helps search products and determine availability by country
Checkout Agent — manages cart operations and payment/checkout rules
Each agent operates under a unique system message to reflect a distinct persona and domain role.

## Requirements

This project requires Python 3.11:
```bash
brew install python@3.11
python3.11 --version
```

## Setup

Create a virtual environment named `venv`:
```bash
cd py-from-zero-to-hero-08
python3.11 -m venv venv
```

Activate it:
```bash
source venv/bin/activate
```

Confirm the environment is active (you should see the `(venv)` prefix):
```text
(venv) renatomatos@PT-D144 py-from-zero-to-hero-08
```

Install dependencies:
```bash
pip install -r ./requirements.txt
```

## Ollama

Run Docker Ollama (port 11435):
```bash
docker run -d --name ollama \
  -p 11435:11434 \
  --network=backend-bridge-network \
  -v ollama:/root/.ollama \
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

You should see something like:
```text
NAME               ID              SIZE      MODIFIED
llama3.2:latest    a80c4f17acd5    2.0 GB    6 minutes ago
```

## Run

```bash
python3.11 src/shopping-cart.py
```

You should see a full integration tool comunication (APIs) between AI agents:
- ShoppingAssistant
- CatalogAgent
- CheckoutAgent

## Sample output

```text
>>>>>>>> USING AUTO REPLY...
ShoppingAssistant (to UserProxy):

You have chosen Lisbon as your delivery city.

Here is your updated cart:
- 2 x Pastel de Nata (€10 each) = €20
- 1 x Bottle of Port Wine (€30)

Your total cost is: €50

Now, let's proceed with the payment process. You have chosen to pay using PayPal.

Please confirm the payment details:

- Payment Method: PayPal
- Amount: €50
- Currency: EUR

Please respond with "CONFIRM" to complete the payment.

--------------------------------------------------------------------------------
UserProxy (to ShoppingAssistant):



--------------------------------------------------------------------------------

>>>>>>>> USING AUTO REPLY...
ShoppingAssistant (to UserProxy):


***** Suggested tool call (call_7ma0vq1z): get_delivery_locations *****
Arguments: 
{"country":"PT"}
***********************************************************************

--------------------------------------------------------------------------------

>>>>>>>> EXECUTING FUNCTION get_delivery_locations...
Call ID: call_7ma0vq1z
Input arguments: {'country': 'PT'}

>>>>>>>> EXECUTED FUNCTION get_delivery_locations...
Call ID: call_7ma0vq1z
Input arguments: {'country': 'PT'}
Output:
{'country': 'PT', 'delivery_locations': [{'country': 'PT', 'city': 'Lisboa', 'region': 'Lisboa'}, {'country': 'PT', 'city': 'Porto', 'region': 'Porto'}, {'country': 'PT', 'city': 'Coimbra', 'region': 'Centro'}, {'country': 'PT', 'city': 'Faro', 'region': 'Algarve'}]}
UserProxy (to ShoppingAssistant):

***** Response from calling tool (call_7ma0vq1z) *****
{'country': 'PT', 'delivery_locations': [{'country': 'PT', 'city': 'Lisboa', 'region': 'Lisboa'}, {'country': 'PT', 'city': 'Porto', 'region': 'Porto'}, {'country': 'PT', 'city': 'Coimbra', 'region': 'Centro'}, {'country': 'PT', 'city': 'Faro', 'region': 'Algarve'}]}
******************************************************

--------------------------------------------------------------------------------

>>>>>>>> USING AUTO REPLY...
ShoppingAssistant (to UserProxy):

Your payment has been successfully processed using PayPal.

Here is your order summary:

- 2 x Pastel de Nata (€10 each) = €20
- 1 x Bottle of Port Wine (€30)
- Total: €50
- Payment Method: PayPal

Your order will be delivered to Lisbon, Portugal within the next 24-48 hours.

TERMINATE
```
