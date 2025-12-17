from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Enum, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class ListingType(str, enum.Enum):
    SELL = "sell"
    FREE = "free"


class ListingStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Images stored as JSON array of URLs
    images = Column(JSON, nullable=False, default=list)
    
    # Foreign keys
    seller_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    language_id = Column(Integer, ForeignKey("languages.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Listing details
    listing_type = Column(Enum(ListingType), nullable=False, default=ListingType.SELL)
    price = Column(Float, nullable=True)  # Nullable if free
    location = Column(String(255), nullable=True, index=True)
    
    # Status
    status = Column(Enum(ListingStatus), nullable=False, default=ListingStatus.PENDING, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    seller = relationship("User", back_populates="books")
    category = relationship("Category", back_populates="books")
    language = relationship("Language", back_populates="books")
    likes = relationship("Like", back_populates="book", cascade="all, delete-orphan")


