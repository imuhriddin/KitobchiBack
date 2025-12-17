from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime
from app.models.book import ListingType, ListingStatus


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    images: List[str] = Field(default_factory=list, max_length=3)
    category_id: Optional[int] = None
    language_id: Optional[int] = None
    listing_type: ListingType
    price: Optional[float] = Field(None, ge=0)
    location: Optional[str] = None
    
    @field_validator("images")
    @classmethod
    def validate_images(cls, v):
        if len(v) > 3:
            raise ValueError("Maximum 3 images allowed")
        return v
    
    @model_validator(mode='after')
    def validate_price_with_listing_type(self):
        """Validate price based on listing type"""
        if self.listing_type == ListingType.SELL and self.price is None:
            raise ValueError("Price is required for sell listings")
        if self.listing_type == ListingType.FREE and self.price is not None:
            raise ValueError("Price must be null for free listings")
        return self


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    images: Optional[List[str]] = Field(None, max_length=3)
    category_id: Optional[int] = None
    language_id: Optional[int] = None
    listing_type: Optional[ListingType] = None
    price: Optional[float] = Field(None, ge=0)
    location: Optional[str] = None
    status: Optional[ListingStatus] = None


class BookResponse(BookBase):
    id: int
    seller_id: int
    status: ListingStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BookDetail(BookResponse):
    """Extended book detail with seller info"""
    seller: "UserProfile"
    category: Optional["CategoryResponse"] = None
    language: Optional["LanguageResponse"] = None
    is_liked: Optional[bool] = False
    
    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    """Response for book list with pagination"""
    items: List[BookResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BookFilterParams(BaseModel):
    """Query parameters for filtering books"""
    category_id: Optional[int] = None
    language_id: Optional[int] = None
    listing_type: Optional[ListingType] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    author: Optional[str] = None
    search: Optional[str] = None  # Search in title and author
    location: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)


# Forward references
from app.schemas.user import UserProfile
from app.schemas.category import CategoryResponse

class LanguageResponse(BaseModel):
    id: int
    name: str
    code: str
    
    class Config:
        from_attributes = True

BookDetail.model_rebuild()

