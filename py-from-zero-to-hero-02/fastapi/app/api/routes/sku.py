from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.schemas.sku import SkuCreate, SkuGetOut, SkuUpdate, SkuOut
from app.uow import sku as crud
from app.uow import uom as uom_crud

router = APIRouter(prefix="/skus", tags=["skus"])

@router.get("", response_model=list[SkuGetOut])
async def list_all(session: AsyncSession = Depends(get_session)):
    return await crud.get_all(session)

@router.post("", response_model=SkuOut, status_code=status.HTTP_201_CREATED)
async def create(payload: SkuCreate, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        uom = await uom_crud.get_by_id(session, payload.uom_id)
        if not uom:
            raise HTTPException(404, "UOM not found")
        code_exists = await crud.get_by_code(session, payload.code)
        if code_exists:
            raise HTTPException(status_code=409, detail="SKU code is already taken")
        description_exists = await crud.get_by_description(session, payload.description)
        if description_exists:
            raise HTTPException(status_code=409, detail="SKU description is already taken")
        return await crud.create(session, payload.code, payload.description, payload.unit_price, payload.uom_id)

@router.put("/{sku_id}", response_model=SkuOut)
async def update(sku_id: int, payload: SkuUpdate, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        obj = await crud.get_by_id(session, sku_id)
        if not obj:
            raise HTTPException(404, "SKU not found")
        next_uom_id = payload.uom_id if payload.uom_id is not None else obj.uom_id
        uom = await uom_crud.get_by_id(session, next_uom_id)
        if not uom:
            raise HTTPException(404, "UOM not found")
        next_code = payload.code if payload.code is not None else obj.code
        next_description = payload.description if payload.description is not None else obj.description
        code_exists = await crud.get_by_code(session, next_code, exclude_id=sku_id)
        if code_exists:
            raise HTTPException(status_code=409, detail="SKU code is already taken")
        description_exists = await crud.get_by_description(
            session, next_description, exclude_id=sku_id
        )
        if description_exists:
            raise HTTPException(status_code=409, detail="SKU description is already taken")
        return await crud.update(
            session, obj, payload.code, payload.description, payload.unit_price, payload.uom_id
        )

@router.delete("/{sku_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(sku_id: int, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        obj = await crud.get_by_id(session, sku_id)
        if not obj:
            raise HTTPException(404, "SKU not found")
        await crud.delete(session, obj)
