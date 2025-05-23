import os
import json
from typing import Optional

from fastapi import Depends, HTTPException, APIRouter, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from models import Book
from db import get_db
from auth import verify_token

router = APIRouter()

class BookInput(BaseModel):
    title: str
    author: str
    date: str | None = Field(max_length=10)
    isbn: str | None = Field(max_length=13)
    amount: int = Field(ge=0, le=100)

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    isbn: Optional[str] = None
    amount: Optional[int] = None


async def create_new_book(book: BookInput, db: Session):
    try:
        # Проверка на существование книги
        exists = db.query(Book).filter_by(title=book.title, author=book.author, date=book.date).count()
        if exists > 0:
            raise HTTPException(status_code=409, detail="Book already exists")
        
        # Создание новой книги
        new_book = Book(
            title=book.title,
            author=book.author,
            date=book.date,
            isbn=book.isbn,
            amount=book.amount
        )
        db.add(new_book)
        db.commit()
        return {
            "status": "success",
            "book": book.title
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

async def get_books(book_id: int, db: Session):
    try:
        if book_id is not None:
            book = db.query(Book).filter(Book.id==book_id).first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            data = [{
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "date": book.date,
                "isbn": book.isbn,
                "amount": book.amount
            }]
        else:
            books = db.query(Book).all()
            data = [{
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "date": book.date,
                "isbn": book.isbn,
                "amount": book.amount
            } for book in books]
        os.makedirs("tables", exist_ok=True)
        with open("tables/books.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

async def update_book(book_id: int, book_data: BookUpdate, db: Session):
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        if book_data.amount is not None:
            if book_data.amount < 0:
                raise HTTPException(status_code=400, detail="Amount cannot be negative")
            book.amount = book_data.amount

        if book_data.title:
            book.title = book_data.title
        if book_data.author:
            book.author = book_data.author
        if book_data.date:
            book.date = book_data.date
        if book_data.isbn:
            exists = db.query(Book).filter_by(isbn=book_data.isbn).count()
            if exists > 0:
                raise HTTPException(status_code=409, detail="ISBN already exists")
            book.isbn = book_data.isbn

        db.commit()
        return {
            "status": "success", 
            "book_id": book.id
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def delete_book(book_id: int, db: Session):
    try:
        book = db.query(Book).filter_by(id=book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        db.delete(book)
        db.commit()
        return {
            "status": "success",
            "book_id": book.id
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/book/create", response_model=dict)
async def book_create_endpoint(book: BookInput, current_user: str = Depends(verify_token), db: Session = Depends(get_db)):
    return await create_new_book(book, db)
@router.get("/book/get", response_model=list)
async def book_get_endpoint(book_id: int | None = Query(default=None), current_user: str = Depends(verify_token), db: Session = Depends(get_db)):
    return await get_books(book_id, db)
@router.put("/book/update/{book_id}", response_model=dict)
async def book_update_endpoint(book_id: int, book_data: BookUpdate, current_user: str = Depends(verify_token), db: Session = Depends(get_db)):
    return await update_book(book_id, book_data, db)
@router.delete("/book/delete/{book_id}", response_model=dict)
async def book_delete_endpoint(book_id: int, current_user: str = Depends(verify_token),db: Session = Depends(get_db)):
    return await delete_book(book_id, db)
