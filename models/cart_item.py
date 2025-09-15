from sqlalchemy import Column, Integer, ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class CartItemDB(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))