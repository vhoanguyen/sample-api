## Installation
```bash
pip install -r requirements.txt
```

## Run
```bash
uvicorn main:app --reload
```

## How to use
 DOC http://127.0.0.1:8000/docs
 1. Login
   ```bash
      curl -X 'POST' \
      'http://127.0.0.1:8000/login' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "username": "string",
      "password": "string"
      }'
   ```
 2. Get all books
   ```bash
      curl -X 'GET' \
      'http://127.0.0.1:8000/books' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer XXX-YYY-ZZZ' \
   ```
 3. Get a single book
   ```bash
      curl -X 'GET' \
      'http://127.0.0.1:8000/book/{isbn}' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer XXX-YYY-ZZZ' \
   ```
 4. Add a new book
   ```bash
      curl -X 'PUT' \
      'http://127.0.0.1:8000/book/asdfa' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -H 'Authorization: Bearer XXX-YYY-ZZZ' \
      -d '{
         "name": "BookA",
         "price": 100,
         "quantity": 20
      }'
   ```
