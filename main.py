from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from fastapi.encoders import jsonable_encoder

from models import Category, TransactionModel, Transaction

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)
valid_transaction_type = ['income', 'expense']


# Create a Teacher
@app.post("/categories/")
def create_category(category: str, db: Session = Depends(get_db)):
    db_category = Category(category=category)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return jsonable_encoder(db_category)


@app.get("/categories/")
def create_category(db: Session = Depends(get_db)):
    return jsonable_encoder(db.query(Category).all())


@app.delete("/categories/{id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(db_category)
    db.commit()
    return jsonable_encoder(db_category)


@app.post("/transactions/")
def create_transaction(transaction: TransactionModel, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.category == transaction.category).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="There are no such category, please add this category first")
    if transaction.type not in valid_transaction_type:
        raise HTTPException(status_code=400, detail=f"Invalid transaction_type: {transaction.type}. "
                                                    f"should be: {valid_transaction_type}")
    db_transaction = Transaction(amount=transaction.amount, type=transaction.type,
                                 category=transaction.category, description=transaction.description,
                                 date=transaction.date, category_id=db_category.id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return jsonable_encoder(db_transaction)


@app.get("/transactions/")
def get_transactions(db: Session = Depends(get_db)):
    return jsonable_encoder(db.query(Transaction).all())


@app.get("/transactions/{id}")
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    return jsonable_encoder(db.query(Transaction).filter(Transaction.id == transaction_id).first())


@app.put("/transactions/{id}")
def update_transaction(transaction_id: int, transaction: TransactionModel, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.category == transaction.category).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="There are no such category, please add this category first")
    if transaction.type not in valid_transaction_type:
        raise HTTPException(status_code=400, detail=f"Invalid transaction_type: {transaction.type}. "
                                                    f"should be: {valid_transaction_type}")
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction was not found")
    db_transaction.amount = transaction.amount
    db_transaction.type = transaction.type
    db_transaction.category = transaction.category
    db_transaction.description = transaction.description
    db_transaction.date = transaction.date
    db_transaction.category_id = db_category.id
    db.commit()
    db.refresh(db_transaction)
    return jsonable_encoder(db_transaction)


@app.delete("/transactions/{id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(db_transaction)
    db.commit()
    return jsonable_encoder(db_transaction)


@app.get("/transactions/search/")
def get_transactions_for_specific(type: str, category: str, start_date: datetime, end_date: datetime,
                                  db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.category == category).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="There are no such category, please add this category first")
    if type not in valid_transaction_type:
        raise HTTPException(status_code=400, detail=f"Invalid transaction_type: {type}. "
                                                    f"should be: {valid_transaction_type}")
    db_transactions = db.query(Transaction).filter(and_(
            Transaction.type == type,
            Transaction.category == category,
            Transaction.date.between(start_date, end_date)
        )).all()
    return jsonable_encoder(db_transactions)
