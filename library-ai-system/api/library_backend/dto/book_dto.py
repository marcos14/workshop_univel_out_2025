from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BookCreate(BaseModel):
    title: str = Field(..., max_length=500)
    isbn: Optional[str] = Field(None, max_length=20)
    publication_year: Optional[int] = None
    publisher: Optional[str] = Field(None, max_length=255)
    language: str = Field(default="Portuguese", max_length=50)
    genre: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    author_names: List[str] = Field(default=[], description="Lista de nomes dos autores")

class BookResponse(BaseModel):
    id: int
    title: str
    isbn: Optional[str]
    publication_year: Optional[int]
    publisher: Optional[str]
    language: str
    pages: Optional[int]
    genre: Optional[str]
    description: Optional[str]
    file_path: Optional[str]
    file_size: Optional[int]
    processed: bool
    created_at: datetime
    updated_at: datetime
    authors: List[str] = Field(default=[])
    
    class Config:
        from_attributes = True

class BookList(BaseModel):
    books: List[BookResponse]
    total: int
    page: int
    per_page: int

class BookUploadResponse(BaseModel):
    success: bool
    message: str
    book_id: Optional[int] = None
    processing_status: str
    task_id: Optional[str] = None