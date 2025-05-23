# Launch instruction

---
## установите библиотеки:
`pip install -r requirements.txt`


## .env
Вам необходимо также создать такой файл в корне проекта:
```
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DATABASE=
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
JWT_TOKEN=<random jwt token>
JWT_ALGORITHM = "<jwt computing alg>"
JWT_ACCESS_TOKEN_EXPIRE=60    
JWT_REFRESH_TOKEN_EXPIRE=10080
```

## Alembic
- `alembic revision --autogenerate -m "your commit"` — добавление новой миграции
- `alembic upgrade head` — применение миграций к базе данных
---

## FastApi
### запуск FastApi локально
`uvicorn main:app --reload --host 0.0.0.0 --port 8000`
### FastApi запросы
#### библиотекарь
##### 1) регистрация библиотекаря
```
curl -X POST http://localhost:8000/librarians_registration \
  -H "Content-Type: application/json" \
  -d '{
        "email": "iceicebabyaf@gmail.com",
        "password": "12345678"
      }'
```
##### 2) логинизация библиотекаря
```
curl -X POST http://localhost:8000/librarians_login \
  -H "Content-Type: application/json" \
  -d '{
        "email": "<email>",
        "password": "<password>"
      }'
```
##### 3) обновление JWT токена
```
curl -X POST http://localhost:8000/refresh_token \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access token>" \
  -d '{}'
```


#### библиотека
##### 1) создание книги
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

##### 2) вывод библиотеки
*вывод одной книги*
```
curl -X GET "http://localhost:8000/book/get/?book_id=<book_id>" \
-H "Authorization: Bearer <access token>"
```
*или вывод всей библиотеки*
```
curl -X GET "http://localhost:8000/book/get" \
-H "Authorization: Bearer <access token>"
```

##### 3) обновление книги
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

##### 4) удаление библиотеки
```
curl -X DELETE http://localhost:8000/book_delete/1 \
-H "Content-Type: application/json" \-H "Authorization: Bearer <access token>"
```


#### Пользователи
##### 1) создание пользователя:
```
curl -X POST http://localhost:8000/user/create \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <access token>" \
-d '{
  "name":"<name>", 
  "email":"<email>"
  }'
```

##### 2) вывод всех пользователей
*вывод одного пользоваетеля*
```
curl -X GET "http://localhost:8000/user/get?user_id=<user_id>" \
-H "Authorization: Bearer <access token>"
```
*или вывод всех*
```
curl -X GET "http://localhost:8000/user/get" \
-H "Authorization: Bearer <access token>"
```

##### 3) обновление пользователя
```
curl -X PUT http://localhost:8000/user/update/1 \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <access token>" \
-d '{
  "name": "<name>"
  }'
```

##### 4) удаление пользователя
```
curl -X DELETE http://localhost:8000/user/delete/1 \
-H "Content-Type: application/json" \-H "Authorization: Bearer <access token>"
```


#### Бизнес логика
##### 1) заимстование книги
```
curl -X POST http://localhost:8000/operation/borrow \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access token>" \
  -d '{
        "book_id": <book id>,
        "user_id": <user id>
      }'
```

##### 2) возврат книги
```
curl -X POST http://localhost:8000/operation/return \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access token>" \
  -d '{
        "book_id": <book id>,
        "user_id": <user id>
      }'
```

##### 3) все операции с книгами
```
curl -X GET "http://localhost:8000/operation/get_all_borrowed_books" \
-H "Authorization: Bearer <access token>"
```

##### 4) книжные задолженности конкретного пользователя:
```
curl -X GET http://localhost:8000/operation//operation/get_unreturned_books \
-H "Content-Type: application/json" \-H "Authorization: Bearer <acces token>"
```

# Project Structure
```
root/
├── alembic.ini
├── auth.py
├── book_manage.py
├── db.py
├── librarians_tokens/
│   ├── librarian1_example_com.json
│   └── librarian2_example_com.json
├── main.py
├── migrations/
│   └── versions/
│       └── [alembic versions...]
├── models.py
├── operations.py
├── tables/
│   ├── all_borrowed_books.json
│   ├── books.json
│   ├── unreturned_books.json
│   └── users.json
├── tests/
│   ├── conftest.py
│   └── test_operations.py
└── users_manage.py
```
## Основные файлы:
- librarians_tokens/ - будут сохраняться библиотекари с их access и refresh токенами
- tables
  - all_borrowed_books.json - все операции, совершенные с книгами
  - books.json - библиотека
  - unreturned_borrowed_books.json - все долги для одного пользователя
  - users.json - список всех пользователей
- main.py - подключение роутеров для:
  - auth.py - регистрация, логинизация(получение JWT токенов), обновление JWT токенов для библиотекарей (админов)
  - book_manage.py - CRUD логика для книг
  - users_manage.py - CRUD логика для пользователей
  - operations.py - бизнес логика
- models.py - описание таблиц с помощью SQLAlchemy ORM
- migrations/versions/ - здесь хранятся все alembic миграции
- alembic.ini:
  в этой строке нужно будет указать данные для бд в таком виде:
  sqlalchemy.url = postgresql://<user>:<password>@<host>:<port>/<database>

# Структура базы данных:
В базе данных PostgreSQL хранится 4 таблицы (их описание находится в models.py)
краткое описание:

- librarians:
  - id - первичный ключ
  - email - должен быть уникальным
  - пароль - считывается при регистрации и сохраняется в хешированном виде

- library:
  -  id - первичный ключ
  -  title - название книги (ненулевое)
  -  author - автор книги (ненулевое)
  -  date - дата выхода книги - принимается в формате: xx.xx.xx/xx.xx.xxxx (либо же любой другой разделитель вместо .)
  -  isbn - уникальный номер книги
  -  amount - количество доступных книг (min:0, max:100- в дальнейшем это значение будет использоваться для логики взятия/возврата книг пользователями)
  -  description - нулевое описание (в миграции изменено на: Not stated для всех книг)

- users:
  - id - первичный ключ
  - name - имя пользователя
  - email - должен быть уникальным

- borrowed_books:
  - id - первичный ключ
  - user_id - ссылается на id из таблицы users
  - book_id - аналогично на таблицу library
  - borrow_date - точная дата взятия пользователем книги
  - return_data - изначально (при взятии) нулевая, при возврате книги - устанавливается на текущую дату (и тогда книга считается возвращенной)


# Бизнес логика:
все операции для эндпоинтов защищены JWT токенами (список всех оперций над книгами защищен JWT так как, по моему мнению, это конфиденциальная информация, и любой человек не должен иметь возможность получить ее)

## Реализация (упрощенно):
#### 1) Взятие книги
#### обращение к таблице library, для поиска соотеветсвующей книге по ее id (+проверка что книга существует):
```python
book = db.query(Book).filter(Book.id==book_id).first()
if not book:
  raise HTTPException(status_code=404, detail="Book not found")
```
#### обращение к таблице users, для поиска соотеветсвующего пользователя по его id (+проверка что пользователь существует):
```python
user = db.query(User).filter(User.id==user_id).first()
if not user:
  raise HTTPException(status_code=404, detail="User not found")
```
#### получение всех невозвращенных книг конкретным пользователем:
`active_books = db.query(BorrowedBooks).filter(BorrowedBooks.user_id==user_id, BorrowedBooks.return_date==None).count()`
#### проверка валидности операции и уменьшение количества экземпляров в библиотеке на 1:
```python
# проверка: пользователь взял и не вернул менее трех книг
if active_books >= 3:
  raise HTTPException(status_code=400, detail="User has already borrowed 3 books")
# провека: книг с необходимым пользователю id >0 в библиотеке
if book.amount <= 0:
  raise HTTPException(status_code=400, detail="Book is not available")
book.amount -= 1
```
#### и далее запись в таблицу borrowed_books с текущими book, user, актуальным временем в borrow_date и указанием о том, что книгу пока не вернули: return_date=None:
```python
  borrowed_book = BorrowedBooks(
      user_id=user_id,
      book_id=book_id,
      borrow_date=datetime.now(),
      return_date=None
  )
```
#### 2) Возврат книги
### аналогично получение книги и пользователя
```python
book = db.query(Book).filter(Book.id==book_id).first()
if not book:
  raise HTTPException(status_code=404, detail="Book not found")
user = db.query(User).filter(User.id==user_id).first()
if not user:
  raise HTTPException(status_code=404, detail="User not found")
```
#### проверка: пользователь мог не брать такую книгу или уже вернуть ее (есть запись в borrowed_books с конкретным book_id, user_id и датой возврата = None):
```
  borrowed = db.query(BorrowedBooks).filter(
      BorrowedBooks.user_id==user.id, 
      BorrowedBooks.book_id==book.id, 
      BorrowedBooks.return_date==None).first()
  if not borrowed:
      raise HTTPException(status_code=400, detail="Such book wasn't borrowed by this user or it was already returned")
```
#### если все ок - количество экземпляров книги в библитеке инкрементируется, и дата возврата устанавливается как текущая дата:
```python
book.amount += 1
borrowed.return_date = datetime.now()
db.commit()
```

# Аунтентификация:
## Реализация:
Реализовано 2 типа токенов: access и refresh
генерация:
в функции `create_access_token`, `create_refresh_token` передается {"sub": user.email}, внутри этих функций получается текущее время и 2 этих параметра передаются в `create_token` где токены кодируются (Время истечения (exp) устанавливается как текущая дата + expires_delta)

Access токен проверяется с помощью функции 'verify_token': декодирует токен (jwt.decode) и проверяет:
- корректность подписи (с использованием JWT_TOKEN и JWT_ALGORITHM)
- тип токена (type == "access")
- наличие поля sub (email)
- если токен недействителен или истек, выбрасывается HTTPException (401)

Refresh - аналогично, с помощью `get_current_user` но с проверкой: type == "refresh"

/librarians_registration - незащищен (регистрирует библиотекаря)
/librarians_login - незащищен (логинит библиотекаря и выдает access, create токены, сохраняя их в соответсвующий файл в /librarians_tokens/_.json)
//refresh_token - защищен (обновление access токена при помощи refresh)(защищен, так как предоставляет access токен который дает права супер пользователя)
для обновления refresh токена - необходимо заново пройти логинизацию.
токены не сохраняются в бд - их валидность проверяется при помощи декодирования и ее валидации. 

## Библиотеки:
- хэширование паролей:
  passlib (pbkdf2_sha256) - простота реализации, большая информационная база об алгоритме, наличие соли, устойчивость к брутфорсу
- JWT
  PYJWT - дефолтная библиотека для работы JWT в python, поддерживает кодирование, декодирование, понятная документация от FastApi

# Что бы я добавил?
- по моему мнению этому проекту не хватает черного списка для токенов и логики делогинизации. в случае утечки access token - у злоумышленника будет некоторое время (например 15 минут), что не есть хорошо. пользователь должен иметь возможность защитить свой аккаунт. однако принцип RESFUL Api при решении такой проблемы с JWT токенами скорее всего не сохранится
- было бы здорово добавить двухфакторку. у меня есть тривиальный алгоритм реализации, но из-за нехватки времени и сложности тестирования для других людей решил не добавлять (нужно создавать GOOGLE APP PASSWORD и привязывать личный gmail) но, конечно в таком виде двухфакторка подойдет только для пет проектов/тестовых заданий

# Буду рад код ревью в каком либо виде

