import asyncio

from shopping_tools import ShoppingTools
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient


def create_shopping_agent() -> ChatAgent:
    """
    Create a Microsoft Agent Framework ChatAgent that uses:
      - Ollama (llama3.2) via OpenAIChatClient
      - Your ShoppingTools methods as function tools
    """

    chat_client = OpenAIChatClient(
        model_id="llama3.2",
        api_key="ollama",
        base_url="http://localhost:11435/v1",
    )

    tools = [
        ShoppingTools.search_products,
        ShoppingTools.get_payment_options,
        ShoppingTools.get_delivery_locations,
        ShoppingTools.add_to_cart,
        ShoppingTools.get_cart,
        ShoppingTools.checkout,
    ]

    instructions = """... same as before ...""".strip()

    agent = ChatAgent(
        chat_client=chat_client,
        name="ShoppingAssistant",
        instructions=instructions,
        tools=tools,
    )

    return agent


async def run_example() -> None:
    agent = create_shopping_agent()
    user_message = (
        "I live in Lisbon, Portugal and I want to buy 2 boxes of Pastel de Nata "
        "and 1 bottle of Port Wine. Show me my cart and then checkout using PayPal."
    )
    result = await agent.run(user_message)
    print(result.text)


if __name__ == "__main__":
    asyncio.run(run_example())
