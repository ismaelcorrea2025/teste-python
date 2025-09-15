from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from models_base import Base

class ProductDB(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)

    cart_items = relationship("CartItemDB", back_populates="product")