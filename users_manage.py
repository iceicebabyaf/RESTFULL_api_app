import os
import json
from typing import Optional

from fastapi import Depends, HTTPException, APIRouter, Query
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session

from models import User
from db import get_db
from auth import verify_token

router = APIRouter()

class UserInput(BaseModel):
    name: str
    email: EmailStr
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

async def create_new_user(user: UserInput, db: Session):
    try:
        exists = db.query(User).filter_by(email=user.email).count()
        if exists > 0:
            raise HTTPException(status_code=409, detail="User already exists")
        
        new_user = User(
            name=user.name,
            email=user.email
        )
        db.add(new_user)
        db.commit()
        return {"status": "success", "email": user.email}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
async def get_users(user_id: int, db: Session):
    try:
        if user_id is not None:
            user = db.query(User).filter(User.id==user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            data = [{
                "name": user.name,
                "email": user.email
            }]
            return data
        else:
            users = db.query(User).all()
            data = [{
                "id": user.id,
                "name": user.name,
                "email": user.email
            } for user in users]
        os.makedirs("tables", exist_ok=True)
        with open("tables/users.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

async def update_user(user_id: int, user_data: UserUpdate, db: Session):
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user_data.name:
            user.name = user_data.name
        if user_data.email:
            exists = db.query(User).filter_by(email=user_data.email).count()
            if exists > 0:
                raise HTTPException(status_code=409, detail="Email already exists")
            user.email = user_data.email
        
        db.commit()
        return {"status": "success", "email": user.email}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def delete_user(user_id: int, db: Session):
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(user)
        db.commit()
        return {"status": "success", "email": user.email}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/user/create", response_model=dict)
async def user_create_endpoint(user: UserInput, current_user: str = Depends(verify_token), db: Session = Depends(get_db)):
    return await create_new_user(user, db)
@router.get("/user/get", response_model=list)
async def user_get_endpoint(user_id: int | None = Query(default=None), current_user: str = Depends(verify_token), db: Session = Depends(get_db)):
    return await get_users(user_id, db)
@router.put("/user/update/{user_id}", response_model=dict)
async def user_update_endpoint(user_id: int, user_data: UserUpdate, current_user: str = Depends(verify_token), db: Session = Depends(get_db)):
    return await update_user(user_id, user_data, db)
@router.delete("/user/delete/{user_id}", response_model=dict)
async def user_delete_endpoint(user_id: int, current_user: str = Depends(verify_token), db: Session = Depends(get_db)):
    return await delete_user(user_id, db)