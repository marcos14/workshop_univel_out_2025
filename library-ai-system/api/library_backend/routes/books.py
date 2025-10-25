from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import asyncio
import logging

from ..database import get_db
from ..models import Book, Author, BookAuthor, BookChunk, User
from ..dto.book_dto import BookCreate, BookResponse, BookList, BookUploadResponse
from ..services.pdf_service import PDFService
from ..services.openai_service import OpenAIService
# from ..services.qdrant_service import QdrantService  # Temporariamente desabilitado
from ..core.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Instanciar serviços
pdf_service = PDFService()
openai_service = OpenAIService()
# qdrant_service = QdrantService()  # Temporariamente desabilitado

@router.post("/upload", response_model=BookUploadResponse)
async def upload_book(
    file: UploadFile = File(...),
    book_data: BookCreate = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload de um livro em PDF"""
    
    # Validar arquivo
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas arquivos PDF são permitidos"
        )
    
    try:
        # Ler conteúdo do arquivo
        file_content = await file.read()
        
        # Validar se é um PDF válido
        if not pdf_service.validate_pdf_file(file_content):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo PDF inválido ou corrompido"
            )
        
        # Gerar nome único para o arquivo
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        upload_dir = os.getenv("UPLOAD_DIR", "/app/uploads")
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Salvar arquivo
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Extrair texto do PDF
        extraction_result = pdf_service.extract_text_from_upload(file_content)
        
        if not extraction_result["success"]:
            # Remover arquivo se extração falhou
            os.unlink(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao processar PDF: {extraction_result['error']}"
            )
        
        # Criar registro do livro no banco
        book = Book(
            title=book_data.title,
            isbn=book_data.isbn,
            publication_year=book_data.publication_year,
            publisher=book_data.publisher,
            language=book_data.language,
            genre=book_data.genre,
            description=book_data.description,
            file_path=file_path,
            file_size=len(file_content),
            pages=extraction_result["total_pages"],
            processed=False
        )
        
        db.add(book)
        db.commit()
        db.refresh(book)
        
        # Criar autores se especificados
        for author_name in book_data.author_names:
            # Verificar se autor já existe
            author = db.query(Author).filter(Author.name == author_name).first()
            if not author:
                author = Author(name=author_name)
                db.add(author)
                db.commit()
                db.refresh(author)
            
            # Associar autor ao livro
            book_author = BookAuthor(book_id=book.id, author_id=author.id)
            db.add(book_author)
        
        db.commit()
        
        # TODO: Processar embeddings em background (temporariamente desabilitado para evitar travamento)
        # asyncio.create_task(process_book_embeddings(book.id, extraction_result))
        
        # Marcar como processado para simplificar
        book.processed = True
        db.commit()
        
        return BookUploadResponse(
            success=True,
            message="Livro enviado com sucesso! Processamento concluído.",
            book_id=book.id,
            processing_status="completed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload do livro: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

# async def process_book_embeddings(book_id: int, extraction_result: dict):
#     """Processar embeddings do livro em background - TEMPORARIAMENTE DESABILITADO"""
#     pass
    # try:
    #     db = next(get_db())
    #     book = db.query(Book).filter(Book.id == book_id).first()
    #     
    #     if not book:
    #         logger.error(f"Livro {book_id} não encontrado para processamento")
    #         return
    #     
    #     # Dividir texto em chunks
    #     full_text = extraction_result["text"]
    #     chunks = openai_service.split_text_by_tokens(full_text, max_tokens=800, overlap=100)
    #     
    #     # Gerar embeddings para cada chunk
    #     embeddings = await openai_service.generate_embeddings_batch(chunks)
    #     
    #     # Salvar chunks e embeddings
    #     for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
    #         if embedding:  # Verificar se embedding foi gerado com sucesso
    #             # Gerar UUID para o ponto no Qdrant
    #             qdrant_point_id = str(uuid.uuid4())
    #             
    #             # Salvar no PostgreSQL
    #             book_chunk = BookChunk(
    #                 book_id=book.id,
    #                 chunk_text=chunk_text,
    #                 chunk_index=idx,
    #                 qdrant_point_id=qdrant_point_id
    #             )
    #             db.add(book_chunk)
    #     
    #     # Marcar livro como processado
    #     book.processed = True
    #     db.commit()
    #     
    #     logger.info(f"Processamento de embeddings concluído para livro {book_id}")
    #     
    # except Exception as e:
    #     logger.error(f"Erro no processamento de embeddings para livro {book_id}: {e}")
    #     # Marcar livro com erro de processamento
    #     try:
    #         db = next(get_db())
    #         book = db.query(Book).filter(Book.id == book_id).first()
    #         if book:
    #             book.processed = False  # Manter como não processado para retry
    #             db.commit()
    #     except:
    #         pass

@router.get("/", response_model=BookList)
async def list_books(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar livros com paginação e filtros"""
    
    query = db.query(Book)
    
    # Aplicar filtros
    if search:
        query = query.filter(Book.title.ilike(f"%{search}%"))
    
    if genre:
        query = query.filter(Book.genre == genre)
    
    # Contar total
    total = query.count()
    
    # Aplicar paginação
    books = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # Converter para resposta
    book_responses = []
    for book in books:
        authors = [ba.author.name for ba in book.book_authors]
        book_response = BookResponse(
            **book.__dict__,
            authors=authors
        )
        book_responses.append(book_response)
    
    return BookList(
        books=book_responses,
        total=total,
        page=page,
        per_page=per_page
    )

@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter detalhes de um livro específico"""
    
    book = db.query(Book).filter(Book.id == book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro não encontrado"
        )
    
    authors = [ba.author.name for ba in book.book_authors]
    
    return BookResponse(
        **book.__dict__,
        authors=authors
    )

@router.delete("/{book_id}")
async def delete_book(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletar um livro e seus dados associados"""
    
    book = db.query(Book).filter(Book.id == book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro não encontrado"
        )
    
    try:
        # TODO: Deletar chunks do Qdrant (temporariamente desabilitado)
        # await qdrant_service.delete_book_chunks(book_id)
        
        # Deletar arquivo físico
        if book.file_path and os.path.exists(book.file_path):
            os.unlink(book.file_path)
        
        # Deletar do banco (cascata deleta chunks, book_authors, etc.)
        db.delete(book)
        db.commit()
        
        return {"message": "Livro deletado com sucesso"}
        
    except Exception as e:
        logger.error(f"Erro ao deletar livro {book_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar livro"
        )