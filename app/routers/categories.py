from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryResponse])
async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    """Get all categories"""
    result = await db.execute(select(Category).order_by(Category.name))
    categories = result.scalars().all()
    return categories


