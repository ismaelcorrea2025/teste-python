from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models_base import Base

class CartItemDB(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))

    user = relationship("UserDB", back_populates="cart_items")
    product = relationship("ProductDB", back_populates="cart_items")