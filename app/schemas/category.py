from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    
    class Config:
        from_attributes = True


