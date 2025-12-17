from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.book import Book, ListingStatus
from app.models.like import Like
from app.schemas.user import UserResponse, UserUpdate, UserProfile
from app.schemas.book import BookResponse, BookListResponse
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfile)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's profile"""
    return current_user


@router.put("/me", response_model=UserProfile)
async def update_my_profile(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update current user's profile"""
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.get("/me/listings", response_model=BookListResponse)
async def get_my_listings(
    status_filter: Optional[ListingStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's book listings"""
    query = select(Book).where(Book.seller_id == current_user.id)
    
    if status_filter:
        query = query.where(Book.status == status_filter)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(Book.created_at.desc())
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    books = result.scalars().all()
    
    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size
    
    return BookListResponse(
        items=books,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/me/saved", response_model=BookListResponse)
async def get_saved_books(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's saved/liked books"""
    # Query books that user has liked
    query = select(Book).join(Like).where(Like.user_id == current_user.id)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(Like.created_at.desc())
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    books = result.scalars().all()
    
    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size
    
    return BookListResponse(
        items=books,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


