import os
import uuid
from typing import List, Optional, Dict
from datetime import datetime
from dataclasses import dataclass
from autogen import ConversableAgent


# === LLM CONFIG ===
config_list = [
    {
        "model": "llama3.2",
        "base_url": "http://localhost:11435/v1",
        "api_key": "ollama",   # not really used, but must not be empty
        "price": [0, 0],       # prompt_price_per_1k, completion_price_per_1k
    },
]

llm_config = {"config_list": config_list, "temperature": 0.0}


# =======================================================================
# Product (Mock for a Product Catalog API response)
# In a real system, this would likely come from a Product Catalog Service
# e.g. GET /products or GET /products/{id}
# =======================================================================

@dataclass
class Product:
    # Unique ID from product catalog
    id: str

    # Product display name (localized if needed)
    name: str

    # Final price (after catalog pricing rules)
    price: float

    # Countries where the product is allowed to be delivered
    available_countries: List[str]

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "available_countries": self.available_countries,
        }

# =======================================================================
# PaymentOption (Mock for a Payments Provider Configuration API)
# In a real system this would come from:
# e.g. GET /payments/options?country=PT
# or a config service describing payment capabilities per region
# =======================================================================

@dataclass
class PaymentOption:
    code: str
    display_name: str
    supported_countries: List[str]

    def to_dict(self):
        return {
            "code": self.code,
            "display_name": self.display_name,
            "supported_countries": self.supported_countries,
        }

# =======================================================================
# DeliveryLocation (Mock for a Logistics / Shipping API response)
# In a real system:
#   - GET /shipping/locations or
#   - GET /shipping/availability?country=PT
# =======================================================================

@dataclass
class DeliveryLocation:
    country: str
    city: str
    region: str

    def to_dict(self):
        return {
            "country": self.country,
            "city": self.city,
            "region": self.region,
        }

# =======================================================================
# CartItem (Mock for a Cart Service API response)
# In a real system:
#   - POST /cart/{id}/items
#   - GET  /cart/{id}
# The cart itself usually lives in Redis, session store, or DB
# =======================================================================

@dataclass
class CartItem:
    product_id: str
    name: str
    unit_price: float
    quantity: int
    country: str

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "name": self.name,
            "unit_price": self.unit_price,
            "quantity": self.quantity,
            "line_total": round(self.unit_price * self.quantity, 2),
            "country": self.country,
        }

# =======================================================================
# OrderSummary (Mock for an Order Processing / Checkout API response)
# In a real system:
#   - POST /orders (during checkout)
#   - GET  /orders/{id}
# =======================================================================

@dataclass
class OrderSummary:
    order_id: str
    cart_id: str
    total_amount: float
    currency: str
    payment_method: str
    delivery_city: str
    delivery_country: str
    created_at: datetime

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "cart_id": self.cart_id,
            "total_amount": self.total_amount,
            "currency": self.currency,
            "payment_method": self.payment_method,
            "delivery_city": self.delivery_city,
            "delivery_country": self.delivery_country,
            "created_at": self.created_at.isoformat(),
        }


# === IN-MEMORY "DATABASE" ===

PRODUCTS: List[Product] = [
    Product(
        id="P001",
        name="Portuguese Olive Oil 500ml",
        price=9.99,
        available_countries=["PT", "ES"],
    ),
    Product(
        id="P002",
        name="Port Wine (Douro DOC)",
        price=19.99,
        available_countries=["PT"],  # Only deliverable in Portugal
    ),
    Product(
        id="P003",
        name="Iberian Ham (Jamón Ibérico)",
        price=39.99,
        available_countries=["ES"],  # Only deliverable in Spain
    ),
    Product(
        id="P004",
        name="Pastel de Nata Box (12 units)",
        price=12.50,
        available_countries=["PT"],
    ),
]

PAYMENT_OPTIONS: List[PaymentOption] = [
    PaymentOption(
        code="paypal",
        display_name="PayPal",
        supported_countries=["PT", "ES"],
    ),
    PaymentOption(
        code="credit_card",
        display_name="Credit Card",
        supported_countries=["PT", "ES"],
    ),
    PaymentOption(
        code="debit_card",
        display_name="Debit Card",
        supported_countries=["PT", "ES"],
    ),
    PaymentOption(
        code="mbway",
        display_name="MB WAY",
        supported_countries=["PT"],  # PT-only method
    ),
]

# We *only* expose Portugal for delivery locations
DELIVERY_LOCATIONS: List[DeliveryLocation] = [
    DeliveryLocation(country="PT", city="Lisboa", region="Lisboa"),
    DeliveryLocation(country="PT", city="Porto", region="Porto"),
    DeliveryLocation(country="PT", city="Coimbra", region="Centro"),
    DeliveryLocation(country="PT", city="Faro", region="Algarve"),
]

# Cart storage (very simple in-memory implementation)
CARTS: Dict[str, List[CartItem]] = {}


# === SHOPPING TOOLS ===

class ShoppingTools:
    """
    Tools that the LLM agents can call to manage products, cart and checkout.
    """

    @staticmethod
    def search_products(
        query: Optional[str] = None,
        country: str = "PT",
    ) -> dict:
        """
        Search for products available for a given country (PT or ES). Optionally filter by query text.
        """
        query_lower = (query or "").lower()

        def matches(product: Product) -> bool:
            if country not in product.available_countries:
                return False
            if not query_lower:
                return True
            return query_lower in product.name.lower()

        results = [p.to_dict() for p in PRODUCTS if matches(p)]
        return {
            "country": country,
            "query": query,
            "products": results,
        }

    @staticmethod
    def get_payment_options(country: str = "PT") -> dict:
        """
        List payment options available for the given country.
        """
        options = [
            p.to_dict()
            for p in PAYMENT_OPTIONS
            if country in p.supported_countries
        ]
        return {
            "country": country,
            "payment_options": options,
        }

    @staticmethod
    def get_delivery_locations(country: str = "PT") -> dict:
        """
        List delivery locations. Checkout is restricted to Portugal (PT).
        If country != 'PT', a warning is returned.
        """
        if country != "PT":
            return {
                "country": country,
                "delivery_locations": [],
                "warning": "Delivery is currently restricted to Portugal (PT) only.",
            }

        locations = [
            loc.to_dict()
            for loc in DELIVERY_LOCATIONS
            if loc.country == "PT"
        ]
        return {
            "country": country,
            "delivery_locations": locations,
        }

    @staticmethod
    def add_to_cart(
        product_id: str,
        quantity: int,
        country: str = "PT",
        cart_id: Optional[str] = None,
    ) -> dict:
        """
        Add a product (with quantity) to a shopping cart for a given country.
        Creates a new cart_id if one is not provided.
        Validates that the product is deliverable to the selected country.
        """
        if quantity <= 0:
            return {"error": "Quantity must be greater than zero."}

        # Find product
        product = next((p for p in PRODUCTS if p.id == product_id), None)
        if product is None:
            return {"error": f"Product '{product_id}' not found."}

        if country not in product.available_countries:
            return {
                "error": (
                    f"Product '{product.name}' (id={product.id}) "
                    f"cannot be delivered to country '{country}'. "
                    f"Available countries: {product.available_countries}"
                )
            }

        # Ensure cart exists
        if not cart_id or cart_id not in CARTS:
            cart_id = uuid.uuid4().hex
            CARTS[cart_id] = []

        cart_items = CARTS[cart_id]

        # Merge with existing item if present
        existing = next(
            (item for item in cart_items if item.product_id == product_id),
            None,
        )
        if existing:
            existing.quantity += quantity
        else:
            cart_items.append(
                CartItem(
                    product_id=product.id,
                    name=product.name,
                    unit_price=product.price,
                    quantity=quantity,
                    country=country,
                )
            )

        total = round(
            sum(item.unit_price * item.quantity for item in cart_items), 2
        )

        return {
            "cart_id": cart_id,
            "items": [i.to_dict() for i in cart_items],
            "total_amount": total,
            "currency": "EUR",
        }

    @staticmethod
    def get_cart(cart_id: str) -> dict:
        """
        Retrieve the current state of a cart.
        """
        if cart_id not in CARTS:
            return {"error": f"Cart '{cart_id}' not found."}

        cart_items = CARTS[cart_id]
        total = round(
            sum(item.unit_price * item.quantity for item in cart_items), 2
        )
        return {
            "cart_id": cart_id,
            "items": [i.to_dict() for i in cart_items],
            "total_amount": total,
            "currency": "EUR",
        }

    @staticmethod
    def checkout(
        cart_id: str,
        payment_method: str,
        delivery_city: str,
        delivery_country: str = "PT",
    ) -> dict:
        """
        Perform a simple checkout:
        - Validates cart exists and is not empty.
        - Enforces that delivery_country is Portugal (PT).
        - Validates payment method is supported for PT.
        """
        if delivery_country != "PT":
            return {
                "error": (
                    "Checkout is restricted to Portugal (PT) only. "
                    f"Provided country: '{delivery_country}'."
                )
            }

        if cart_id not in CARTS or not CARTS[cart_id]:
            return {"error": f"Cart '{cart_id}' is empty or does not exist."}

        # Validate payment method for PT
        payment = next(
            (
                p
                for p in PAYMENT_OPTIONS
                if p.code == payment_method and "PT" in p.supported_countries
            ),
            None,
        )
        if payment is None:
            return {
                "error": (
                    f"Payment method '{payment_method}' is not available "
                    "for Portugal (PT)."
                )
            }

        cart_items = CARTS[cart_id]
        total = round(
            sum(item.unit_price * item.quantity for item in cart_items), 2
        )

        order = OrderSummary(
            order_id=uuid.uuid4().hex,
            cart_id=cart_id,
            total_amount=total,
            currency="EUR",
            payment_method=payment.display_name,
            delivery_city=delivery_city,
            delivery_country=delivery_country,
            created_at=datetime.now(),
        )

        # In a real system, we might clear the cart or mark it as completed.
        # Here we keep it in memory and just return the order summary.
        return {
            "order": order.to_dict(),
            "items": [i.to_dict() for i in cart_items],
        }


# === TERMINATION CHECK (same pattern as your code) ===

def check_termination(msg):
    try:
        content = msg.get("content", "")
        if isinstance(content, str):
            if "TERMINATE" in content or any(
                term in content.lower()
                for term in ["completed", "here is the summary", "finished"]
            ):
                return True
        return False
    except Exception:
        return False


# === MULTI-AGENT SHOPPING CART SYSTEM ===

class ShoppingCartSystem:
    def __init__(self, llm_config: dict):
        self.tools = ShoppingTools()

        agents = {
            "shopping_assistant": (
                "ShoppingAssistant",
                (
                    "You are a helpful AI shopping assistant. "
                    "You help the user browse products, pick payment options, "
                    "select a delivery city in Portugal, manage the cart, "
                    "and complete checkout. Add 'TERMINATE' when the task is complete."
                ),
            ),
            "catalog_agent": (
                "CatalogAgent",
                (
                    "You specialize in product discovery and availability by country. "
                    "Use the tools to search for products and explain which countries "
                    "they can be delivered to. Add 'TERMINATE' when you are done."
                ),
            ),
            "checkout_agent": (
                "CheckoutAgent",
                (
                    "You handle cart management and checkout. "
                    "Use tools to add items to the cart, review the cart, "
                    "and perform checkout with valid payment methods and "
                    "delivery locations (Portugal only). Add 'TERMINATE' when done."
                ),
            ),
        }

        for attr, (name, sys_msg) in agents.items():
            setattr(
                self,
                attr,
                ConversableAgent(
                    name=name,
                    system_message=sys_msg,
                    llm_config=llm_config,
                ),
            )

        self.user_proxy = ConversableAgent(
            name="UserProxy",
            is_termination_msg=check_termination,
            human_input_mode="NEVER",
        )

        self._register_tools()

    def _register_tools(self):
        tools = [
            self.tools.search_products,
            self.tools.get_payment_options,
            self.tools.get_delivery_locations,
            self.tools.add_to_cart,
            self.tools.get_cart,
            self.tools.checkout,
        ]

        # Register tools for LLM invocation + for actual execution
        for tool in tools:
            # LLM side (the “thinking” agent)
            self.shopping_assistant.register_for_llm(
                name=tool.__name__,
                description=tool.__doc__ or f"Execute {tool.__name__}",
            )(tool)
            self.catalog_agent.register_for_llm(
                name=tool.__name__,
                description=tool.__doc__ or f"Execute {tool.__name__}",
            )(tool)
            self.checkout_agent.register_for_llm(
                name=tool.__name__,
                description=tool.__doc__ or f"Execute {tool.__name__}",
            )(tool)

            # Execution side (the tool runner)
            self.user_proxy.register_for_execution(name=tool.__name__)(tool)

    def initiate_conversation(self, message: str):
        """
        Starts a conversation with the main shopping assistant.
        """
        return self.user_proxy.initiate_chat(
            self.shopping_assistant,
            message=message,
        )


if __name__ == "__main__":
    shopping_system = ShoppingCartSystem(llm_config)

    # Example conversation:
    # The agent should:
    #  - find products deliverable to PT
    #  - suggest payment options
    #  - pick a delivery city in Portugal
    #  - add items to the cart and perform checkout
    shopping_system.initiate_conversation(
        "I live in Lisbon, Portugal and I want to buy 2 boxes of Pastel de Nata "
        "and 1 bottle of Port Wine. Show me my cart and then checkout using PayPal."
    )
