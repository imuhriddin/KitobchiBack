# Kitobchi Backend API

A production-ready FastAPI backend for Kitobchi - an online marketplace for buying, selling, and giving away books.

## Tech Stack

- **Python 3.10+**
- **FastAPI** - Modern, fast web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy 2.0** (async) - ORM
- **Alembic** - Database migrations
- **JWT** - Authentication
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## Features

### Authentication (Priority 1)
- ✅ User registration
- ✅ Login with JWT access token
- ✅ Logout (token-based)
- ✅ Password hashing (bcrypt)
- ✅ Password reset (stubbed for future implementation)

### Book Listing / Homepage (Priority 2)
- ✅ Get all books (public)
- ✅ Book card data (cover, title, author, price, location)
- ✅ Filtering (category, price range, author, language)
- ✅ Search by title and author
- ✅ Pagination

### Create Book Listing (Priority 3)
- ✅ Authenticated users can create listings
- ✅ Up to 3 images (URLs)
- ✅ Listing types: sell or free
- ✅ Listing status: pending, approved, rejected

### Book Detail Page (Priority 4)
- ✅ Full book information
- ✅ Seller profile (name, phone, telegram)
- ✅ Book images and description

### User Profile (Priority 5)
- ✅ Get and update profile
- ✅ My listings (active, rejected, archived)
- ✅ Saved books (liked)

### Likes / Saved Books (Priority 6)
- ✅ Like / unlike book
- ✅ Get list of saved books

## Project Structure

```
KitobchiBack/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── book.py
│   │   ├── category.py
│   │   ├── language.py
│   │   └── like.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── book.py
│   │   ├── category.py
│   │   ├── language.py
│   │   ├── like.py
│   │   └── auth.py
│   ├── routers/                # API endpoints
│   │   ├── auth.py
│   │   ├── books.py
│   │   ├── users.py
│   │   ├── likes.py
│   │   ├── categories.py
│   │   └── languages.py
│   └── utils/                  # Utilities
│       ├── security.py         # JWT, password hashing
│       └── dependencies.py    # FastAPI dependencies
├── alembic/                    # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── alembic.ini                 # Alembic configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd KitobchiBack
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/kitobchi_db

# JWT Settings
SECRET_KEY=your-secret-key-here-change-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App Settings
DEBUG=True
PROJECT_NAME=Kitobchi
API_V1_PREFIX=/api/v1
```

**Important:** Generate a secure SECRET_KEY for production:
```bash
# Linux/Mac
openssl rand -hex 32

# Windows (PowerShell)
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

### 5. Create PostgreSQL Database

```sql
CREATE DATABASE kitobchi_db;
```

Or using command line:
```bash
createdb kitobchi_db
```

### 6. Run Database Migrations

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 7. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `POST /api/v1/auth/logout` - Logout
- `POST /api/v1/auth/password-reset` - Password reset (stubbed)

### Books
- `GET /api/v1/books` - Get all books (with filtering, search, pagination)
- `POST /api/v1/books` - Create book listing (authenticated)
- `GET /api/v1/books/{book_id}` - Get book detail
- `PUT /api/v1/books/{book_id}` - Update book (owner only)
- `DELETE /api/v1/books/{book_id}` - Delete book (owner only)

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user profile
- `GET /api/v1/users/me/listings` - Get my listings
- `GET /api/v1/users/me/saved` - Get saved books

### Likes
- `POST /api/v1/likes` - Like a book
- `DELETE /api/v1/likes/{book_id}` - Unlike a book

### Categories
- `GET /api/v1/categories` - Get all categories

### Languages
- `GET /api/v1/languages` - Get all languages

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. After logging in, include the token in the Authorization header:

```
Authorization: Bearer <your-access-token>
```

## Database Models

### Users
- id, email (unique), password (hashed), first_name, last_name, phone, telegram_username, avatar_url, bio, created_at

### Books
- id, title, author, description, images (JSON array), seller_id, category_id, language_id, listing_type (sell/free), price, location, status (pending/approved/rejected), created_at, updated_at

### Categories
- id, name, slug

### Languages
- id, name, code

### Likes
- id, user_id, book_id, created_at (unique constraint on user_id + book_id)

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

### Code Style

The project follows PEP 8 style guidelines. Consider using:
- `black` for code formatting
- `flake8` or `ruff` for linting
- `mypy` for type checking

## Production Deployment

### Security Checklist

1. ✅ Change `SECRET_KEY` to a strong random value
2. ✅ Set `DEBUG=False`
3. ✅ Configure CORS with specific origins
4. ✅ Use environment variables for sensitive data
5. ✅ Enable HTTPS
6. ✅ Set up proper database backups
7. ✅ Configure rate limiting
8. ✅ Set up logging and monitoring

### Environment Variables for Production

```env
DEBUG=False
SECRET_KEY=<strong-random-key>
DATABASE_URL=<production-database-url>
```

### Running with Gunicorn (Production)

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Future Enhancements

- [ ] Password reset with email verification
- [ ] Email notifications
- [ ] Image upload (currently using URLs)
- [ ] Admin panel for book approval
- [ ] Chat/messaging feature
- [ ] Book recommendations
- [ ] Advanced search with full-text search
- [ ] Rate limiting
- [ ] Caching with Redis
- [ ] Unit and integration tests

## License

[Your License Here]

## Support

For issues and questions, please open an issue on the repository.


