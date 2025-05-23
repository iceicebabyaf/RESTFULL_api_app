import os
import json
from typing import Optional
from datetime import datetime

from fastapi import Depends, HTTPException, APIRouter, Query
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session

from models import Book, User, BorrowedBooks
from db import get_db
from auth import verify_token

router = APIRouter()

class BorrowBookInput(BaseModel):
    book_id: int = Field(ge=0)
    user_id: int = Field(ge=0)


async def borrow_book(book_id: int, user_id: int, db: Session):
    try:
        book = db.query(Book).filter(Book.id==book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        user = db.query(User).filter(User.id==user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        active_books = db.query(BorrowedBooks).filter(BorrowedBooks.user_id==user_id, BorrowedBooks.return_date==None).count()
        if active_books >= 3:
            raise HTTPException(status_code=400, detail="User has already borrowed 3 books")
        if book.amount <= 0:
            raise HTTPException(status_code=400, detail="Book is not available")
        book.amount -= 1

        borrowed_book = BorrowedBooks(
            user_id=user_id,
            book_id=book_id,
            borrow_date=datetime.now(),
            return_date=None
        )

        db.add(borrowed_book)
        db.commit()

        return {
            "status": "success", 
            "book": book.title, "book id": book_id,
            "user": user.name, "user id": user_id
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    

async def return_book(book_id: int, user_id: int, db: Session):
    try:
        book = db.query(Book).filter(Book.id==book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        user = db.query(User).filter(User.id==user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        borrowed = db.query(BorrowedBooks).filter(
            BorrowedBooks.user_id==user.id, 
            BorrowedBooks.book_id==book.id, 
            BorrowedBooks.return_date==None).first()
        
        if not borrowed:
            raise HTTPException(status_code=400, detail="Such book wasn't borrowed by this user or it was already returned")
        book.amount += 1

        borrowed.return_date = datetime.now()
        db.commit()
        return {"status": "success",
                "book": book.title, "book id": book_id,
                "user": user.name, "user id": user_id,
                "return_date": borrowed.return_date
                }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
async def get_all_borrowed_books(db: Session):
    try:
        borrowed_books = db.query(BorrowedBooks).all()
        data = [{
            "user_id": borrowed.user_id,
            "book_id": borrowed.book_id,
            "borrow_date": str(borrowed.borrow_date),
            "return_date": str(borrowed.return_date) if borrowed.return_date else None
        } for borrowed in borrowed_books]
        
        os.makedirs("tables", exist_ok=True)
        with open("tables/all_borrowed_books.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
async def get_unreturned_books(user_id: str, db: Session):
    try:
        user = db.query(User).filter(User.id==user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        borrowed_books = db.query(BorrowedBooks).filter(
            BorrowedBooks.user_id==user.id, 
            BorrowedBooks.return_date==None).all()
        data = [{
            "user_id": borrowed.user_id,
            "book_id": borrowed.book_id,
            "borrow_date": str(borrowed.borrow_date),
            "return_date": None
        } for borrowed in borrowed_books]
        os.makedirs("tables", exist_ok=True)
        with open("tables/unreturned_books.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        return {"operation": "success", 
                "unreturned_books": data
                }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/operation/borrow", response_model=dict)
async def borrow_book_endpoint(input_data: BorrowBookInput, current_user: str=Depends(verify_token),  db: Session = Depends(get_db)):
    return await borrow_book(input_data.book_id, input_data.user_id, db)
@router.post("/operation/return", response_model=dict)
async def return_book_endpoint(input_data: BorrowBookInput, current_user: str=Depends(verify_token), db: Session = Depends(get_db)):
    return await return_book(input_data.book_id, input_data.user_id, db)
@router.get("/operation/get_all_borrowed_books", response_model=list[dict])
async def get_all_borrowed_books_endpoint(current_user: str = Depends(verify_token), db: Session = Depends(get_db)):
    return await get_all_borrowed_books(db)
@router.get("/operation/get_unreturned_books/{user_id}", response_model=dict)
async def get_unreturned_books_endpoint(user_id: int, current_user: str = Depends(verify_token), db: Session = Depends(get_db)):
    return await get_unreturned_books(user_id, db)