from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models_base import Base

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    cart_items = relationship("CartItemDB", back_populates="user")