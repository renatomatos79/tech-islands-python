from pydantic import BaseModel

# Define the order output schema to be used by the prompt
class OrderInfo(BaseModel):
  is_order: bool
  order_id: int


# Define the scope output schema to be used by the prompt
class ScopeInfo(BaseModel):
  is_scoped: bool
  answer: str