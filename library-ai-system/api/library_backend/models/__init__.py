from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, Float, ARRAY, JSON, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    interactions = relationship("UserBookInteraction", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("BookRecommendation", back_populates="user", cascade="all, delete-orphan")

class Author(Base):
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    biography = Column(Text)
    birth_date = Column(Date)
    death_date = Column(Date)
    nationality = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    book_authors = relationship("BookAuthor", back_populates="author")

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    isbn = Column(String(20), unique=True)
    publication_year = Column(Integer)
    publisher = Column(String(255))
    language = Column(String(50), default="Portuguese")
    pages = Column(Integer)
    genre = Column(String(100))
    description = Column(Text)
    file_path = Column(String(500))
    file_size = Column(BigInteger)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    book_authors = relationship("BookAuthor", back_populates="book", cascade="all, delete-orphan")
    chunks = relationship("BookChunk", back_populates="book", cascade="all, delete-orphan")
    interactions = relationship("UserBookInteraction", back_populates="book", cascade="all, delete-orphan")
    recommendations = relationship("BookRecommendation", back_populates="book", cascade="all, delete-orphan")

class BookAuthor(Base):
    __tablename__ = "book_authors"
    
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id", ondelete="CASCADE"), nullable=False)
    
    # Relacionamentos
    book = relationship("Book", back_populates="book_authors")
    author = relationship("Author", back_populates="book_authors")

class BookChunk(Base):
    __tablename__ = "book_chunks"
    
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer)
    qdrant_point_id = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    book = relationship("Book", back_populates="chunks")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    books_referenced = Column(ARRAY(Integer))  # Array de IDs de livros
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    conversation = relationship("Conversation", back_populates="messages")

class UserBookInteraction(Base):
    __tablename__ = "user_book_interactions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    interaction_type = Column(String(50), nullable=False)  # 'view', 'download', 'search', 'chat_reference'
    metadata_info = Column(JSON)  # Dados adicionais sobre a interação
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    user = relationship("User", back_populates="interactions")
    book = relationship("Book", back_populates="interactions")

class BookRecommendation(Base):
    __tablename__ = "book_recommendations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    reason = Column(Text)  # Motivo da recomendação
    confidence_score = Column(Float)  # Score de confiança (0-1)
    created_at = Column(DateTime, default=datetime.utcnow)
    clicked = Column(Boolean, default=False)
    clicked_at = Column(DateTime)
    
    # Relacionamentos
    user = relationship("User", back_populates="recommendations")
    book = relationship("Book", back_populates="recommendations")