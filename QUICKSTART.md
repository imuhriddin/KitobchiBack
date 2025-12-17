# Quick Start Guide

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Set Up Environment

Create a `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/kitobchi_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
PROJECT_NAME=Kitobchi
API_V1_PREFIX=/api/v1
```

## 3. Create Database

```bash
# PostgreSQL
createdb kitobchi_db

# Or using psql
psql -U postgres -c "CREATE DATABASE kitobchi_db;"
```

## 4. Run Migrations

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## 5. Run the Server

```bash
uvicorn app.main:app --reload
```

## 6. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Test the API

### Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Get Books (Public)

```bash
curl "http://localhost:8000/api/v1/books?page=1&page_size=10"
```

### Create a Book Listing (Authenticated)

```bash
curl -X POST "http://localhost:8000/api/v1/books" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "description": "A classic American novel",
    "images": ["https://example.com/cover.jpg"],
    "listing_type": "sell",
    "price": 15.99,
    "location": "Tashkent"
  }'
```


