from pydantic import BaseModel

# Define the schema for the response
class OrderInfo(BaseModel):
  is_order: bool
  order_id: int


# Define the schema for the response
class ScopeInfo(BaseModel):
  is_scoped: bool
  answer: str