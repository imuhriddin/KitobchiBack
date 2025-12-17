from pydantic import BaseModel
from datetime import datetime
from app.schemas.book import BookResponse


class LikeCreate(BaseModel):
    book_id: int


class LikeResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    created_at: datetime
    book: BookResponse
    
    class Config:
        from_attributes = True


