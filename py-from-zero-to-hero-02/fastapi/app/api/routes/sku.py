from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.schemas.sku import SkuCreate, SkuUpdate, SkuOut
from app.uow import sku as crud

router = APIRouter(prefix="/skus", tags=["skus"])

@router.get("", response_model=list[SkuOut])
async def list_all(session: AsyncSession = Depends(get_session)):
    return await crud.get_all(session)

@router.post("", response_model=SkuOut, status_code=status.HTTP_201_CREATED)
async def create(payload: SkuCreate, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        return await crud.create(session, payload.code, payload.description, payload.unit_price, payload.uom_id)

@router.put("/{sku_id}", response_model=SkuOut)
async def update(sku_id: int, payload: SkuUpdate, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        obj = await crud.get_by_id(session, sku_id)
        if not obj:
            raise HTTPException(404, "SKU not found")
        return await crud.update(session, obj, payload.description, payload.unit_price, payload.uom_id)

@router.delete("/{sku_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(sku_id: int, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        obj = await crud.get_by_id(session, sku_id)
        if not obj:
            raise HTTPException(404, "SKU not found")
        await crud.delete(session, obj)