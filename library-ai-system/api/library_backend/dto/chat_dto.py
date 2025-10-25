from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    books_referenced: Optional[List[int]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)

class ConversationResponse(BaseModel):
    id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class ConversationWithMessages(BaseModel):
    id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]
    
    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    conversation_id: int
    message: MessageResponse
    context_books: List[str] = Field(default=[], description="Livros utilizados como contexto")

class SimpleChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    search_books: bool = Field(default=False, description="Buscar contexto nos livros")

class SimpleChatResponse(BaseModel):
    message: str
    response: str
    search_books: bool
    context_books: List[str] = Field(default=[], description="Livros utilizados como contexto")