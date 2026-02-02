from mcp.server.fastmcp import FastMCP
from random import choice
from typing import List, Dict, Optional, Literal

mcp = FastMCP("random_name")

# --------------------------
# Initial tool
# --------------------------
@mcp.tool()
def get_random_name(names: list = []) -> str:
    """Gets a random peoples names. The names are stored in a local array
    args:
       names:the user can pass in a list of names to choose from, or it will default to a predefined list.
    """
    if len(names) > 0:
        return choice(names)
    return choice(["Alice","Bob","Charlie","Diana","Eve","Frank","Grace","Hank","Ivy","Jack"])

# --------------------------
# Hardcoded customers dataset
# --------------------------
CUSTOMERS: List[Dict[str, object]] = [
    {"id": 1, "name": "Ana Silva", "countryCode": "PT"},
    {"id": 2, "name": "Bruno Costa", "countryCode": "PT"},
    {"id": 3, "name": "Carla Souza", "countryCode": "BR"},
    {"id": 4, "name": "Diego Santos", "countryCode": "BR"},
    {"id": 5, "name": "Emma Johnson", "countryCode": "US"},
    {"id": 6, "name": "Frank Miller", "countryCode": "US"},
    {"id": 7, "name": "Giulia Rossi", "countryCode": "IT"},
    {"id": 8, "name": "Hiro Tanaka", "countryCode": "JP"},
    {"id": 9, "name": "Inês Almeida", "countryCode": "PT"},
    {"id": 10, "name": "Juan Pérez", "countryCode": "ES"},
]


# --------------------------
# New tool 1: search customers (filter by ids)
# --------------------------
@mcp.tool()
def customers_search(ids: List[int] = []) -> List[Dict[str, object]]:
    """Returns a hardcoded list of customers.
    args:
        ids: optional list of customer IDs to filter by. If empty, returns all customers.
    returns:
        A JSON array of customers: [{"id": int, "name": str, "countryCode": str}, ...]
    """
    if not ids:
        return CUSTOMERS

    ids_set = set(ids)
    return [c for c in CUSTOMERS if c["id"] in ids_set]

# --------------------------
# New tool 2: get customer by id
# --------------------------
@mcp.tool()
def customers_get_by_id(id: int) -> Optional[Dict[str, object]]:
    """Returns a single customer by ID from the hardcoded list.
    args:
        id: customer ID
    returns:
        A single customer object or None if not found
    """
    for c in CUSTOMERS:
        if c["id"] == id:
            return c
    return None

# --------------------------
# ✅ NEW TOOL 3: search by names (partial match)
# --------------------------
@mcp.tool()
def customers_search_by_names(names: List[str] = []) -> List[Dict[str, object]]:
    """
    Search customers by name (case-insensitive, partial match).
    
    args:
      names: list of name fragments to search for 
              e.g. ["ana", "silva", "john"].
              If empty, returns all customers.
    """
    if not names:
        return CUSTOMERS

    # normalize search terms
    terms = [n.lower() for n in names]

    result = []
    for c in CUSTOMERS:
        customer_name = c["name"].lower()
        if any(term in customer_name for term in terms):
            result.append(c)

    return result


# ============================================================
# ✅ NEW: Orders tool
# ============================================================

OrderStatus = Literal["pending", "prepared", "deliverying", "canceled", "done"]

# Hardcoded orders dataset
ORDERS: List[Dict[str, object]] = [
    {
        "customerID": 1,
        "orderDate": "2026-01-10T11:15:00Z",
        "orderValue": 24.90,
        "description": "Haircut + beard trim",
        "status": "done",
    },
    {
        "customerID": 1,
        "orderDate": "2026-01-28T16:40:00Z",
        "orderValue": 12.50,
        "description": "Beard trim",
        "status": "prepared",
    },
    {
        "customerID": 2,
        "orderDate": "2026-01-22T09:05:00Z",
        "orderValue": 19.99,
        "description": "Haircut",
        "status": "done",
    },
    {
        "customerID": 3,
        "orderDate": "2026-01-30T13:20:00Z",
        "orderValue": 49.00,
        "description": "Hair treatment package",
        "status": "pending",
    },
    {
        "customerID": 5,
        "orderDate": "2026-01-05T18:00:00Z",
        "orderValue": 89.90,
        "description": "Premium grooming kit",
        "status": "deliverying",
    },
    {
        "customerID": 5,
        "orderDate": "2026-01-25T10:00:00Z",
        "orderValue": 15.00,
        "description": "Shampoo refill",
        "status": "canceled",
    },
    {
        "customerID": 7,
        "orderDate": "2026-01-12T14:10:00Z",
        "orderValue": 29.50,
        "description": "Beard styling + wax",
        "status": "done",
    },
    {
        "customerID": 9,
        "orderDate": "2026-01-18T12:00:00Z",
        "orderValue": 22.00,
        "description": "Haircut + wash",
        "status": "done",
    },
]

_ALLOWED_STATUSES = {"pending", "prepared", "deliverying", "canceled", "done"}

OrderStatus = Literal["pending", "prepared", "deliverying", "canceled", "done"]

@mcp.tool()
def customer_orders_get(customerID: int) -> List[Dict[str, object]]:
    """
    Fetch orders for a given customer.

    args:
      customerID: customer id

    returns:
      JSON array of orders with:
        customerID: int
        orderDate: ISO 8601 datetime string
        orderValue: decimal (float for now)
        description: string
        status: "pending" | "prepared" | "deliverying" | "canceled" | "done"
    """
    # Filter only orders belonging to the customer
    result = [o for o in ORDERS if o["customerID"] == customerID]

    # Optional: ensure status values are valid (defensive)
    for o in result:
        if o.get("status") not in _ALLOWED_STATUSES:
            o["status"] = "pending"

    return result

@mcp.tool()
def customer_orders_by_status(status: OrderStatus) -> List[Dict[str, object]]:
    """
    Fetch orders filtered by status.

    args:
      status: one of 
        "pending" | "prepared" | "deliverying" | "canceled" | "done"

    returns:
      JSON array of orders matching that status, each containing:
        customerID: int
        orderDate: ISO 8601 datetime string
        orderValue: decimal (float)
        description: string
        status: string
    """

    if status not in _ALLOWED_STATUSES:
        raise ValueError(f"Invalid status: {status}")

    return [o for o in ORDERS if o["status"] == status]