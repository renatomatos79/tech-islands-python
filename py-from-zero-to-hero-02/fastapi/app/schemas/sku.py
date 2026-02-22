from pydantic import BaseModel
from app.schemas.uom import UomOut

class SkuCreate(BaseModel):
    """Payload for creating a SKU."""

    code: str
    description: str
    unit_price: float
    uom_id: int

class SkuUpdate(BaseModel):
    """Payload for partial SKU updates."""

    code: str | None = None
    description: str | None = None
    unit_price: float | None = None
    uom_id: int | None = None

class SkuOut(BaseModel):
    """Default SKU response used by write endpoints."""

    id: int
    code: str
    description: str
    unit_price: float
    uom_id: int

    #  it enables response_model to serialize SQLAlchemy entities directly.
    model_config = {"from_attributes": True}


class SkuGetOut(BaseModel):
    """SKU read response with nested UOM object."""

    id: int
    code: str
    description: str
    unit_price: float
    uom: UomOut

    #  it enables response_model to serialize SQLAlchemy entities directly.
    model_config = {"from_attributes": True}
