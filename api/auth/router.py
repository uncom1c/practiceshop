from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from psycopg2 import IntegrityError

from config import JWT_ALGORITHM, JWT_SECRET
from services.schemas import TokenData
from .schemas import (
    UserCreate,
    Token,
    user_base,
)
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import user_table
from jose import JWTError
import jwt

# from sqlalchemy.exc import *

from services.user_service import (
    assign_role,
    get_username,
    service_login_for_access_token,
    encode_user,
    service_register_handler,
    
)
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_async_session),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_username(token_data.username, db)
    if user is None:
        raise credentials_exception
    return user

@router.get("/me", response_model=None)
async def me_handler(user: Annotated[user_base, Depends(get_current_user)]):
    return user

@router.post("/register")
async def register_handler(
    user_create: UserCreate, db: AsyncSession = Depends(get_async_session)
):
    try:
        user = await service_register_handler(user_create, db)
    except BaseException as _ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=_ex
        )

    return user

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_async_session),
) -> Token:
    print(1)
    try:
        jwt = await service_login_for_access_token(form_data, db)
    except BaseException as _ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=_ex
        )

    return jwt