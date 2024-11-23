from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship

from database import Base
from pydantic import BaseModel

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)

    transaction = relationship("Transaction", back_populates="category_relationship",
                               cascade="all, delete, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer, index=True)
    type = Column(String, index=True)
    category = Column(String, index=True)
    description = Column(String, index=True)
    date = Column(DateTime(timezone=True))
    category_id = Column(Integer, ForeignKey('categories.id'))

    category_relationship = relationship("Category", back_populates="transaction")


class TransactionModel(BaseModel):
    amount: int
    type: str
    category: str
    description: str
    date: datetime
