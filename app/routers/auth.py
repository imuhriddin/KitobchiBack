from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, Token
from app.schemas.user import UserResponse
from app.utils.security import verify_password, get_password_hash, create_access_token
from datetime import timedelta
from app.config import settings
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    clean_password = user_data.password.strip()
    
    try:
        hashed_password = get_password_hash(clean_password)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Password is too long (max 64 characters)"
        )

    new_user = User(
        email=user_data.email,
        password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    except Exception as e:
        await db.rollback()
        # vaqtincha ko‘rish uchun
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    # Userni topamiz
    result = await db.execute(
        select(User).where(User.email == login_data.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Token yaratamiz
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

