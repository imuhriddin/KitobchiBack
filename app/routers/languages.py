from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.language import Language
from app.schemas.book import LanguageResponse

router = APIRouter(prefix="/languages", tags=["Languages"])


@router.get("", response_model=list[LanguageResponse])
async def get_languages(
    db: AsyncSession = Depends(get_db)
):
    """Get all languages"""
    result = await db.execute(select(Language).order_by(Language.name))
    languages = result.scalars().all()
    return languages


