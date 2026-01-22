import uuid
from typing import List, Optional, Dict
from datetime import datetime
from dataclasses import dataclass

# =======================================================================
# PAY ATTENTION!
# This is the same file content from folder 08... 
# However without the autogen package
# =======================================================================

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
