from fastapi import APIRouter
# from sqlalchemy.exc import *

router = APIRouter()







# @router.post("/login")
# async def login_handler(user_login: User_login, db: AsyncSession = Depends(get_async_session)):

#     result = await get_email(user_login.email, db)

#     if not result:
#         return "no such user"

#     if not verify_password(user_login.password, result["password"]):
#         return "wrong password"

#     # generate jwt
#     # return jwt
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     jwt_token =  create_access_token(data={"sub": result["username"]}, expires_delta=access_token_expires)

#     return Token(access_token = jwt_token, token_type="bearer")



@router.get("/zalupa")
async def zalupa_handler():
    return "hello world"









