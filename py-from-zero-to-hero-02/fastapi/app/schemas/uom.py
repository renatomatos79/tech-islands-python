from pydantic import BaseModel

class UomCreate(BaseModel):
    """Payload for creating a unit of measurement."""

    code: str
    name: str    

class UomUpdate(BaseModel):
    """Payload for partial unit-of-measurement updates."""

    code: str | None = None
    name: str | None = None    

class UomOut(BaseModel):
    """Unit-of-measurement response schema."""

    id: int
    code: str
    name: str    

    model_config = {"from_attributes": True}
