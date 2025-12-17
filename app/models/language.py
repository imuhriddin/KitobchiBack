from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Language(Base):
    __tablename__ = "languages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    
    # Relationships
    books = relationship("Book", back_populates="language")


