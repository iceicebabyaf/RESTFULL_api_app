from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Librarian(Base):
    __tablename__ = "librarians"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

class Book(Base):
    __tablename__ = "library"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    date = Column(String(10))
    isbn = Column(String(13), unique=True)
    amount = Column(Integer, nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)

class BorrowedBooks(Base):
    __tablename__ = "borrowed_books"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("library.id"), nullable=False)
    borrow_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=True)