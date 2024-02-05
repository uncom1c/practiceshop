from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from psycopg2 import IntegrityError
from db.schemas import (
    UserCreate,
    Token,
    user_base,
)
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import user_table
# from sqlalchemy.exc import *

from services.user_service import (
    service_login_for_access_token,
    encode_user,
    get_current_user
)
router = APIRouter()

@router.get("/me", response_model=None)
async def me_handler(user: Annotated[user_base, Depends(get_current_user)]):
    return user

@router.post("/register")
async def register_handler(
    user_create: UserCreate, db: AsyncSession = Depends(get_async_session)
):
    user_create = encode_user(user_create)
    query = user_table.insert().values(**user_create.dict())

    try:
        inserted_user = await db.execute(query)
    except IntegrityError:
        return "такой пользователь уже есть, ХУЕСОС"

    await db.commit()

    return (
        f"Поздравляем, вы зарегались, пользователь {inserted_user.inserted_primary_key}"
    )


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_async_session),
) -> Token:
    try:
        jwt = await service_login_for_access_token(form_data, db)
    except BaseException as _ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=_ex
        )

    return jwt