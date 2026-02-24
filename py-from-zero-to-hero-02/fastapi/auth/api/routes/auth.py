from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.api.deps import get_session
from auth.models.user import User
from auth.schemas.auth import RegisterIn, TokenOut
from auth.uow import user as svc
from auth.util.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register(payload: RegisterIn, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        existing_by_email = await svc.get_by_email(session, payload.email)
        if existing_by_email:
            raise HTTPException(409, "Email is already taken")

        existing_by_username = await svc.get_by_username(session, payload.username)
        if existing_by_username:
            raise HTTPException(409, "Username is already taken")
        
        pwd = hash_password(payload.password)

        user = User(
            username=payload.username,
            email=payload.email,
            password_hash=pwd,
            role="user",
        )
        session.add(user)
        await session.flush()

        return {"id": user.id, "email": user.email, "role": user.role}


@router.post("/token", response_model=TokenOut)
async def token(
    payload: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    async with session.begin():
        user = await svc.get_by_username(session, payload.username)
        if user == None:
           raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials! (username)")
        
        if user.is_active == False:
           raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials! (is_active)")
    
        if not verify_password(payload.password, user.password_hash):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials! (password)")

        token = create_access_token(sub=user.email, role=user.role)
        return TokenOut(access_token=token)