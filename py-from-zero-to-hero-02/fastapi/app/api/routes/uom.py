from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.schemas.uom import UomCreate, UomUpdate, UomOut
from app.uow import uom as crud
from app.uow import sku as sku_crud

router = APIRouter(prefix="/unit-of-measurements", tags=["unit_of_measurements"])

@router.get("", response_model=list[UomOut])
async def list_all(session: AsyncSession = Depends(get_session)):
    return await crud.get_all(session)

@router.post("", response_model=UomOut, status_code=status.HTTP_201_CREATED)
async def create(payload: UomCreate, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        code_exists = await crud.get_by_code(session, payload.code)
        if code_exists:
            raise HTTPException(status_code=409, detail="UOM code is already taken")
        name_exists = await crud.get_by_name(session, payload.name)
        if name_exists:
            raise HTTPException(status_code=409, detail="UOM description is already taken")
        return await crud.create(session, payload.name, payload.code)

@router.put("/{uom_id}", response_model=UomOut, status_code=status.HTTP_200_OK)
async def update(uom_id: int, payload: UomUpdate, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        obj = await crud.get_by_id(session, uom_id)
        if not obj:
            raise HTTPException(404, "UOM not found")
        next_code = payload.code if payload.code is not None else obj.code
        next_name = payload.name if payload.name is not None else obj.name
        code_exists = await crud.get_by_code(session, next_code, exclude_id=uom_id)
        if code_exists:
            raise HTTPException(status_code=409, detail="UOM code is already taken")
        name_exists = await crud.get_by_name(session, next_name, exclude_id=uom_id)
        if name_exists:
            raise HTTPException(status_code=409, detail="UOM description is already taken")
        return await crud.update(session, obj, payload.name, payload.code)

@router.delete("/{uom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(uom_id: int, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        obj = await crud.get_by_id(session, uom_id)
        if not obj:
            raise HTTPException(404, "UOM not found")
        sku_exists = await sku_crud.has_any_for_uom(session, uom_id)
        if sku_exists:
            raise HTTPException(
                status_code=409,
                detail="Cannot delete UOM because it is used by one or more SKUs",
            )
        await crud.delete(session, obj)     
