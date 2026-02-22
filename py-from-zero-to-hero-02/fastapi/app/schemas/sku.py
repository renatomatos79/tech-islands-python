from pydantic import BaseModel

class SkuCreate(BaseModel):
    code: str
    description: str
    unit_price: float
    uom_id: int

class SkuUpdate(BaseModel):
    code: str | None = None
    description: str | None = None
    unit_price: float | None = None
    uom_id: int | None = None

class SkuOut(BaseModel):
    id: int
    code: str
    description: str
    unit_price: float
    uom_id: int

    model_config = {"from_attributes": True}
