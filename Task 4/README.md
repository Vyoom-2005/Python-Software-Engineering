# FastAPI / Flask Microservice with JWT Authentication

Secure Notes REST microservice built with FastAPI, Pydantic, SQLAlchemy, SQLite, bcrypt and JWT.

## Endpoints
Public: `GET /health`, `POST /register`, `POST /login`.
Protected: `GET /me`, `POST /notes`, `GET /notes`, `GET /notes/{id}`, `PUT /notes/{id}`, `DELETE /notes/{id}`.

## Run
```bash
python -m venv .venv
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```
Swagger: `http://127.0.0.1:8000/docs`.

## Test
```bash
pytest -q
```

Passwords are bcrypt-hashed; JWTs expire; protected CRUD is restricted to the authenticated owner. SQLite is the default persistence layer and can be switched to PostgreSQL with `DATABASE_URL` and a PostgreSQL driver.

Import `postman/FastAPI-JWT-Microservice.postman_collection.json` into Postman for API testing.
