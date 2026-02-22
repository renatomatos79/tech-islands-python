from pydantic import BaseModel

class UomCreate(BaseModel):
    code: str
    name: str    

class UomUpdate(BaseModel):
    code: str | None = None
    name: str | None = None    

class UomOut(BaseModel):
    id: int
    code: str
    name: str    

    model_config = {"from_attributes": True}