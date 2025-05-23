from datetime import datetime, timedelta, timezone
import os
import json

import re
import jwt
from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr
from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import pbkdf2_sha256
from sqlalchemy.orm import Session

from models import Librarian
from db import get_db

router = APIRouter()


class UserInput(BaseModel):
    email: EmailStr
    password: str

class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


load_dotenv()
jwt_token = os.getenv("JWT_TOKEN")
jwt_algorithm = os.getenv("JWT_ALGORITHM")
jwt_access_te = os.getenv("JWT_ACCESS_TOKEN_EXPIRE")
jwt_refresh_te = os.getenv("JWT_REFRESH_TOKEN_EXPIRE")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="librarians_login")



def normalize_email_for_filename(email: str) -> str:
    return re.sub(r"[^\w]", "_", email)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, jwt_token, algorithms=[jwt_algorithm])
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, jwt_token, algorithms=[jwt_algorithm])
        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload["sub"]
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def create_access_token(data: dict):
    expires_delta = timedelta(minutes=int(jwt_access_te))
    return create_token(data, expires_delta, "access")

def create_refresh_token(data: dict):
    expires_delta = timedelta(minutes=int(jwt_refresh_te))
    return create_token(data, expires_delta, "refresh")

def create_token(data: dict, expires_delta: timedelta, token_type: str):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({
        "exp": expire,
        "type": token_type
    })
    encoded_jwt = jwt.encode(to_encode, jwt_token, algorithm=jwt_algorithm)
    return encoded_jwt


async def registrate(email: str, hashed_password: str, db: Session):
    try:
        exists = db.query(Librarian).filter_by(email=email).count()
        if exists > 0:
            raise HTTPException(status_code=409, detail="Email already exists")
        
        new_librarian = Librarian(email=email, hashed_password=hashed_password)
        db.add(new_librarian)
        db.commit()
        return {"status": "success", "email": email}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

async def login(user: UserInput, db: Session) -> Tokens:
    try:
        librarian = db.query(Librarian).filter_by(email=user.email).first()
        if not librarian:
            raise HTTPException(status_code=401, detail="Invalid email")
        
        if not pbkdf2_sha256.verify(user.password, librarian.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid password")
        
        token_data = {"sub": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        os.makedirs("librarians_tokens", exist_ok=True)
        data = [{
            "user": user.email,
            "access_token": access_token,
            "refresh_token": refresh_token
        }]
        filename = normalize_email_for_filename(user.email)
        with open("librarians_tokens/"+str(filename)+".json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        return Tokens(access_token=access_token, refresh_token=refresh_token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/librarians_registration", response_model=dict)
async def user_registration_endpoint(user: UserInput, db: Session = Depends(get_db)):
    hashed_password = pbkdf2_sha256.hash(user.password)
    return await registrate(user.email, hashed_password, db)

@router.post("/librarians_login", response_model=Tokens)
async def user_login_endpoint(user: UserInput, db: Session = Depends(get_db)):
    return await login(user, db)

@router.post("/refresh_token", response_model=Tokens)
async def refresh_token_endpoint(token: str = Depends(oauth2_scheme)):
    email = await get_current_user(token)
    token_data = {"sub": email}
    new_access_token = create_access_token(token_data)
    os.makedirs("librarians_tokens", exist_ok=True)
    data = [{
        "user": email,
        "access_token": new_access_token,
        "refresh_token": token
    }]
    filename = normalize_email_for_filename(email)
    with open("librarians_tokens/"+str(filename)+".json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    return Tokens(access_token=new_access_token, refresh_token=token, token_type="bearer")