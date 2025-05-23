# запуск FastApi
`uvicorn main:app --reload --host 0.0.0.0 --port 8000`

# Alembic
`alembic revision --autogenerate -m "your commit"` -- добавление новой версии в migrations
`alembic upgrade head` ------------------------------ обновление бд PostgreSQL

# библиотекарь
1) регистрация библиотекаря
```
curl -X POST http://localhost:8000/librarians_registration \
  -H "Content-Type: application/json" \
  -d '{
        "email": "iceicebabyaf@gmail.com",
        "password": "12345678"
      }'
```
2) логинизация библиотекаря
```
curl -X POST http://localhost:8000/librarians_login \
  -H "Content-Type: application/json" \
  -d '{
        "email": "<email>",
        "password": "<password>"
      }'
```
3) обновление JWT токена
```
curl -X POST http://localhost:8000/refresh_token \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access token>" \
  -d '{}'
```


# библиотека
1) создание книги
```
curl -X POST http://localhost:8000/book/create \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <access token>" \
-d '{
  "title":"<title>",
  "author":"<author>",
  "date":"<date: xx.xx.xx/xx.xx.xxxx>",
  "isbn":"<isbn>",
  "amount":<amount>
  }'
```

2) вывод библиотеки
### вывод книги
```
curl -X GET "http://localhost:8000/book/get/?book_id=<book_id>" \
-H "Authorization: Bearer <access token>"
```
### или вывод всей библиотеки
```
curl -X GET "http://localhost:8000/book/get" \
-H "Authorization: Bearer <access token>"
```

3) обновление книги
```
curl -X PUT http://localhost:8000/book/update/1 \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <access token>" \
-d '{
  "title": "<title>",
  "author": "<author>",
  "date": "<date: xx.xx.xx/xx.xx.xxxx>",
  "isbn": "<isbn>",
  "amount": <amount>
}'
```

4) удаление библиотеки
```
curl -X DELETE http://localhost:8000/book_delete/1 \
-H "Content-Type: application/json" \-H "Authorization: Bearer <access token>"
```


# Пользователи
1) создание пользователя:
```
curl -X POST http://localhost:8000/user/create \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <access token>" \
-d '{
  "name":"<name>", 
  "email":"<email>"
  }'
```

2) вывод всех пользователей
### вывод одного пользоваетеля
```
curl -X GET "http://localhost:8000/user/get?user_id=<user_id>" \
-H "Authorization: Bearer <access token>"
```
### или для вывода всех:
```
curl -X GET "http://localhost:8000/user/get" \
-H "Authorization: Bearer <access token>"
```

3) обновление пользователя
```
curl -X PUT http://localhost:8000/user/update/1 \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <access token>" \
-d '{
  "name": "<name>"
  }'
```

4) удаление пользователя
```
curl -X DELETE http://localhost:8000/user/delete/1 \
-H "Content-Type: application/json" \-H "Authorization: Bearer <access token>"
```


# Бизнес логика
1) заимстование книги
```
curl -X POST http://localhost:8000/operation/borrow \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access token>" \
  -d '{
        "book_id": <book id>,
        "user_id": <user id>
      }'
```

2) возврат книги
```
curl -X POST http://localhost:8000/operation/return \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access token>" \
  -d '{
        "book_id": <book id>,
        "user_id": <user id>
      }'
```

3) все операции с книгами
```
curl -X GET "http://localhost:8000/operation/get_all_borrowed_books" \
-H "Authorization: Bearer <access token>"
```

4) книжные задолженности конкретного пользователя:
```
curl -X GET http://localhost:8000/operation//operation/get_unreturned_books \
-H "Content-Type: application/json" \-H "Authorization: Bearer <acces token>"
```

