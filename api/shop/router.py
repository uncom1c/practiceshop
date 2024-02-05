from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from db.schemas import (
    buy_form,
    user_base,
)
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.exc import *

from services.user_service import (
    service_add_item,
    get_current_user,
    buy_service
)
router = APIRouter()

@router.post("/add_item")
async def add_item(item_name, db: AsyncSession = Depends(get_async_session)):
    try:
        added = await service_add_item(item_name, db)
    except BaseException as _ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=_ex
        )


    return added


@router.post("/buy")
async def buy_handler(
    item: buy_form,
    user: Annotated[user_base, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_session),
):
    try:
        order_create = await buy_service(
            item, user, db
        )
    except BaseException as _ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=_ex
        )
    return order_create
