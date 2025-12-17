from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from typing import Optional
from app.database import get_db
from app.models.book import Book, ListingType, ListingStatus
from app.models.user import User
from app.models.category import Category
from app.models.language import Language
from app.models.like import Like
from app.schemas.book import (
    BookCreate, BookUpdate, BookResponse, BookDetail, BookListResponse, BookFilterParams
)
from app.schemas.user import UserProfile
from app.schemas.category import CategoryResponse
from app.utils.dependencies import get_current_active_user
from app.models.user import User as UserModel

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=BookListResponse)
async def get_books(
    params: BookFilterParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Get all books with filtering, search, and pagination"""
    # Start building query - only show approved books for public
    query = select(Book).where(Book.status == ListingStatus.APPROVED)
    
    # Apply filters
    if params.category_id:
        query = query.where(Book.category_id == params.category_id)
    
    if params.language_id:
        query = query.where(Book.language_id == params.language_id)
    
    if params.listing_type:
        query = query.where(Book.listing_type == params.listing_type)
    
    if params.min_price is not None:
        query = query.where(Book.price >= params.min_price)
    
    if params.max_price is not None:
        query = query.where(Book.price <= params.max_price)
    
    if params.author:
        query = query.where(Book.author.ilike(f"%{params.author}%"))
    
    if params.location:
        query = query.where(Book.location.ilike(f"%{params.location}%"))
    
    if params.search:
        search_term = f"%{params.search}%"
        query = query.where(
            or_(
                Book.title.ilike(search_term),
                Book.author.ilike(search_term)
            )
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (params.page - 1) * params.page_size
    query = query.order_by(Book.created_at.desc())
    query = query.offset(offset).limit(params.page_size)
    
    # Execute query
    result = await db.execute(query)
    books = result.scalars().all()
    
    # Calculate total pages
    total_pages = (total + params.page_size - 1) // params.page_size
    
    return BookListResponse(
        items=books,
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=total_pages
    )


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Create a new book listing"""
    # Validate category if provided
    if book_data.category_id:
        result = await db.execute(select(Category).where(Category.id == book_data.category_id))
        category = result.scalar_one_or_none()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    
    # Validate language if provided
    if book_data.language_id:
        result = await db.execute(select(Language).where(Language.id == book_data.language_id))
        language = result.scalar_one_or_none()
        if not language:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Language not found"
            )
    
    # Create book
    new_book = Book(
        **book_data.model_dump(),
        seller_id=current_user.id,
        status=ListingStatus.PENDING
    )
    
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    
    return new_book


@router.get("/{book_id}", response_model=BookDetail)
async def get_book_detail(
    book_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get book detail with seller information"""
    # Load book with relationships
    query = select(Book).options(
        selectinload(Book.seller),
        selectinload(Book.category),
        selectinload(Book.language)
    ).where(Book.id == book_id)
    
    result = await db.execute(query)
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Check if user liked this book (will be false for unauthenticated users)
    is_liked = False
    
    # Build response using model_validate for proper serialization
    from app.schemas.book import LanguageResponse
    
    # Create response dict
    book_dict = {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "description": book.description,
        "images": book.images,
        "category_id": book.category_id,
        "language_id": book.language_id,
        "listing_type": book.listing_type,
        "price": book.price,
        "location": book.location,
        "seller_id": book.seller_id,
        "status": book.status,
        "created_at": book.created_at,
        "updated_at": book.updated_at,
        "seller": UserProfile.model_validate(book.seller),
        "category": CategoryResponse.model_validate(book.category) if book.category else None,
        "language": LanguageResponse.model_validate(book.language) if book.language else None,
        "is_liked": is_liked
    }
    
    return BookDetail(**book_dict)


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Update a book listing (only by owner)"""
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    if book.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this book"
        )
    
    # Update fields
    update_data = book_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)
    
    await db.commit()
    await db.refresh(book)
    
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Delete a book listing (only by owner)"""
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    if book.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this book"
        )
    
    await db.delete(book)
    await db.commit()
    
    return None

