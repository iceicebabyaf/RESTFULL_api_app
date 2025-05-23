from fastapi import FastAPI
from auth import router as auth_router
from book_manage import router as book_manage_router
from users_manage import router as user_manage_router


app = FastAPI()
app.include_router(auth_router)
app.include_router(book_manage_router)
app.include_router(user_manage_router)
