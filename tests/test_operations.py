import pytest
from datetime import datetime

from fastapi import status

from models import Book, User, BorrowedBooks
from auth import create_access_token


@pytest.fixture
def sample_user(db_session):
    user = User(name="Test User", email="testuser@example.com")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def sample_book(db_session):
    book = Book(
        title="Test Book",
        author="Author Name",
        date="2000-01-01",
        isbn="1234567890123",
        amount=2
    )
    db_session.add(book)
    db_session.commit()
    return book

def get_auth_header_for_user(email: str):
    token_data = {"sub": email}
    access_token = create_access_token(token_data)
    return {"Authorization": f"Bearer {access_token}"}

def test_borrow_success(client, sample_user, sample_book, db_session):
    assert sample_book.amount == 2

    payload = {
        "book_id": sample_book.id,
        "user_id": sample_user.id
    }
    headers = get_auth_header_for_user(sample_user.email)

    response = client.post("/operation/borrow", json=payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status"] == "success"
    assert (data.get("book id") == sample_book.id)
    assert (data.get("user id") == sample_user.id)

    updated_book = db_session.query(Book).get(sample_book.id)
    assert updated_book.amount == 1

    borrow_record = (
        db_session.query(BorrowedBooks)
        .filter(
            BorrowedBooks.book_id == sample_book.id,
            BorrowedBooks.user_id == sample_user.id,
            BorrowedBooks.return_date.is_(None)
        )
        .first()
    )
    assert borrow_record is not None

def test_borrow_no_copies(client, sample_user, db_session):
    book = Book(
        title="No copies Book",
        author="Author Name",
        date="2000-01-01",
        isbn="0000000000000",
        amount=0
    )
    db_session.add(book)
    db_session.commit()

    payload = {"book_id": book.id, "user_id": sample_user.id}
    headers = get_auth_header_for_user(sample_user.email)

    response = client.post("/operation/borrow", json=payload, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Book is not available" in response.json()["detail"]

def test_borrow_exceed_limit(client, sample_user, sample_book, db_session):
    for _ in range(3):
        bb = BorrowedBooks(
            user_id=sample_user.id,
            book_id=sample_book.id,
            borrow_date=datetime.utcnow(),
            return_date=None
        )
        db_session.add(bb)
    sample_book.amount = 5
    db_session.commit()

    payload = {"book_id": sample_book.id, "user_id": sample_user.id}
    headers = get_auth_header_for_user(sample_user.email)

    response = client.post("/operation/borrow", json=payload, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already borrowed 3 books" in response.json()["detail"]


@pytest.fixture
def borrowed_pair(db_session, sample_user, sample_book):
    borrowed = BorrowedBooks(
        user_id=sample_user.id,
        book_id=sample_book.id,
        borrow_date=datetime.utcnow(),
        return_date=None
    )
    sample_book.amount -= 1
    db_session.add_all([borrowed, sample_book])
    db_session.commit()
    return borrowed

def test_return_success(client, borrowed_pair, sample_user, sample_book, db_session):
    assert sample_book.amount == 1

    payload = {"book_id": sample_book.id, "user_id": sample_user.id}
    headers = get_auth_header_for_user(sample_user.email)

    response = client.post("/operation/return", json=payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status"] == "success"

    updated_borrow = db_session.query(BorrowedBooks).get(borrowed_pair.id)
    assert updated_borrow.return_date is not None

    updated_book = db_session.query(Book).get(sample_book.id)
    assert updated_book.amount == 2

def test_return_not_borrowed(client, sample_user, sample_book):
    payload = {"book_id": sample_book.id, "user_id": sample_user.id}
    headers = get_auth_header_for_user(sample_user.email)

    response = client.post("/operation/return", json=payload, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "wasn't borrowed" in response.json()["detail"]

def test_get_all_borrowed_books_empty(client):
    response = client.get("/operation/get_all_borrowed_books", headers=get_auth_header_for_user("testuser@example.com"))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert data == []

def test_get_all_borrowed_books_with_data(client, db_session, sample_user, sample_book):
    bb1 = BorrowedBooks(
        user_id=sample_user.id,
        book_id=sample_book.id,
        borrow_date=datetime.utcnow(),
        return_date=None
    )
    bb2 = BorrowedBooks(
        user_id=sample_user.id,
        book_id=sample_book.id,
        borrow_date=datetime.utcnow(),
        return_date=datetime.utcnow()
    )
    db_session.add_all([bb1, bb2])
    db_session.commit()

    headers = get_auth_header_for_user(sample_user.email)
    response = client.get("/operation/get_all_borrowed_books", headers=headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    for rec in data:
        assert "user_id" in rec
        assert "book_id" in rec
        assert "borrow_date" in rec
        assert "return_date" in rec

def test_get_unreturned_books_empty(client, sample_user):
    headers = get_auth_header_for_user(sample_user.email)
    response = client.get(f"/operation/get_unreturned_books/{sample_user.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, dict)
    assert data["operation"] == "success"
    assert isinstance(data["unreturned_books"], list)
    assert data["unreturned_books"] == []

def test_get_unreturned_books_with_data(client, db_session, sample_user, sample_book):
    bb_active = BorrowedBooks(
        user_id=sample_user.id,
        book_id=sample_book.id,
        borrow_date=datetime.utcnow(),
        return_date=None
    )
    bb_returned = BorrowedBooks(
        user_id=sample_user.id,
        book_id=sample_book.id,
        borrow_date=datetime.utcnow(),
        return_date=datetime.utcnow()
    )
    db_session.add_all([bb_active, bb_returned])
    db_session.commit()

    headers = get_auth_header_for_user(sample_user.email)
    response = client.get(f"/operation/get_unreturned_books/{sample_user.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["operation"] == "success"
    unreturned = data["unreturned_books"]

    assert isinstance(unreturned, list)
    assert len(unreturned) == 1
    rec = unreturned[0]
    assert rec["user_id"] == sample_user.id
    assert rec["book_id"] == sample_book.id
    assert rec["return_date"] is None
