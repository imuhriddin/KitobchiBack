from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.database import get_db
from app.models.user import User
from app.models.book import Book
from app.models.like import Like
from app.schemas.like import LikeCreate, LikeResponse
from app.schemas.book import BookResponse
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/likes", tags=["Likes"])


@router.post("", response_model=LikeResponse, status_code=status.HTTP_201_CREATED)
async def like_book(
    like_data: LikeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Like a book"""
    # Check if book exists
    result = await db.execute(select(Book).where(Book.id == like_data.book_id))
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Check if already liked
    existing_like = await db.execute(
        select(Like).where(
            and_(Like.user_id == current_user.id, Like.book_id == like_data.book_id)
        )
    )
    if existing_like.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book already liked"
        )
    
    # Create like
    new_like = Like(
        user_id=current_user.id,
        book_id=like_data.book_id
    )
    
    db.add(new_like)
    await db.commit()
    await db.refresh(new_like)
    
    # Load book for response
    await db.refresh(new_like, ["book"])
    
    return LikeResponse(
        id=new_like.id,
        user_id=new_like.user_id,
        book_id=new_like.book_id,
        created_at=new_like.created_at,
        book=BookResponse.model_validate(book)
    )


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Unlike a book"""
    result = await db.execute(
        select(Like).where(
            and_(Like.user_id == current_user.id, Like.book_id == book_id)
        )
    )
    like = result.scalar_one_or_none()
    
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found"
        )
    
    await db.delete(like)
    await db.commit()
    
    return None


