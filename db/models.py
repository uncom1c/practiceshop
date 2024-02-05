from sqlalchemy import MetaData, Integer, String, TIMESTAMP, ForeignKey, Table, Column, JSON, Boolean, PickleType

from datetime import date, datetime, timedelta
from .base import metadata


item_table = Table(
    "item",
    metadata,
    Column("id", Integer, index= True, primary_key=True),
    Column("name", String, index=True, unique=True , nullable=False),
    Column("cost", Integer, nullable=False),
    Column("quantity", Integer, nullable=False)


)

user_table = Table(
    "user",
    metadata,
    Column("id", Integer, index=True, primary_key=True),
    Column("email", String, unique=True, nullable=False),
    Column("username", String, index=True, unique=True, nullable=False),
    Column("password", String, nullable=False),
    Column("money", Integer, default=1000 ),
)

order_table = Table(
    "order",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id"), index=True ,nullable=False),
    Column("item_id", Integer, ForeignKey("item.id"), nullable=False),
    Column("quantity", Integer, nullable=False)
)

# class UserManager():
#     reset_password_token_secret = SECRET
#     verification_token_secret = SECRET

#     async def on_after_register(self, user: user, request: Optional[Request] = None):
#         print(f"User {user.id} has registered.")

#     def start(self, request =Request ):
#         self.request: Request = request
#         self.errors: List = []
#         self.username: Optional[str] = None
#         self.email: Optional[str] = None
#         self.password: Optional[str] = None
    
#     async def getting_data(self):
#         form = self.request.form

#     async def validation(self):