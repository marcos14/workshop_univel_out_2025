from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import asyncio
import logging
import json

from ..database import get_db
from ..models import Book, Author, BookAuthor, BookChunk, User
from ..dto.book_dto import BookCreate, BookResponse, BookList, BookUploadResponse
from ..services.pdf_service import PDFService
from ..services.openai_service import OpenAIService
from ..services.qdrant_service import QdrantService
from ..core.auth import get_current_user
from ..tasks.embeddings_tasks import process_pdf_embeddings, search_similar_documents
from ..tasks.demo_tasks import demo_process_embeddings
from ..celery_app import celery_app
from celery.result import AsyncResult

logger = logging.getLogger(__name__)
router = APIRouter()

# Instanciar serviços
pdf_service = PDFService()
openai_service = OpenAIService()
qdrant_service = QdrantService()  # Reativado para uso com Celery

@router.post("/upload", response_model=BookUploadResponse)
async def upload_book(
    file: UploadFile = File(...),
    title: str = Query(...),
    isbn: Optional[str] = Query(None),
    publication_year: Optional[int] = Query(None),
    publisher: Optional[str] = Query(None),
    language: str = Query("Portuguese"),
    genre: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    author_names: str = Query("[]"),  # JSON string para lista
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
            title=title,
            isbn=isbn,
            publication_year=publication_year,
            publisher=publisher,
            language=language,
            genre=genre,
            description=description,
            file_path=file_path,
            file_size=len(file_content),
            pages=extraction_result["total_pages"],
            processed=False
        )
        
        db.add(book)
        db.commit()
        db.refresh(book)
        
        # Criar autores se especificados
        try:
            author_list = json.loads(author_names) if author_names != "[]" else []
        except json.JSONDecodeError:
            author_list = [author_names] if author_names else []
            
        for author_name in author_list:
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
        
        # Processar embeddings usando Celery (assíncrono)
        try:
            # Criar chunks do texto
            chunks = pdf_service.create_text_chunks(extraction_result["text"])
            
            # Enviar task para Celery
            task = process_pdf_embeddings.delay(book.id, chunks)
            
            # Salvar task ID no banco para tracking
            book.task_id = task.id
            db.commit()
            
            logger.info(f"Task de embeddings iniciada para livro {book.id}: {task.id}")
            
            return BookUploadResponse(
                success=True,
                message="Livro enviado com sucesso! Processamento de embeddings iniciado.",
                book_id=book.id,
                processing_status="processing",
                task_id=task.id
            )
            
        except Exception as e:
            logger.warning(f"Erro ao iniciar processamento de embeddings: {e}")
            # Marcar como processado sem embeddings se houver erro
            book.processed = True
            db.commit()
            
            return BookUploadResponse(
                success=True,
                message="Livro enviado com sucesso! (Processamento de embeddings com erro)",
                book_id=book.id,
                processing_status="completed_with_errors"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload do livro: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

async def process_book_embeddings(book_id: int, extraction_result: dict):
    """Processar embeddings do livro em background - versão segura"""
    try:
        # Criar nova sessão de banco para o background task
        from ..database import SessionLocal
        db = SessionLocal()
        
        try:
            book = db.query(Book).filter(Book.id == book_id).first()
            
            if not book:
                logger.error(f"Livro {book_id} não encontrado para processamento")
                return
            
            logger.info(f"Iniciando processamento de embeddings para livro {book_id}: {book.title}")
            
            # Dividir texto em chunks
            full_text = extraction_result["text"]
            if not full_text or len(full_text.strip()) == 0:
                logger.warning(f"Texto vazio para o livro {book_id}")
                book.processed = True
                db.commit()
                return
                
            chunks = openai_service.split_text_by_tokens(full_text, max_tokens=800, overlap=100)
            logger.info(f"Texto dividido em {len(chunks)} chunks")
            
            # Verificar se há OPENAI_API_KEY
            import os
            if not os.getenv("OPENAI_API_KEY"):
                logger.warning("OPENAI_API_KEY não encontrada, pulando geração de embeddings")
                book.processed = True
                db.commit()
                return
            
            # Gerar embeddings para cada chunk
            embeddings = await openai_service.generate_embeddings_batch(chunks)
            logger.info(f"Gerados {len([e for e in embeddings if e])} embeddings válidos")
            
            # Salvar chunks e embeddings
            chunks_salvos = 0
            for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                if embedding:  # Verificar se embedding foi gerado com sucesso
                    # Gerar UUID para o ponto no Qdrant
                    qdrant_point_id = str(uuid.uuid4())
                    
                    # Salvar no PostgreSQL
                    book_chunk = BookChunk(
                        book_id=book.id,
                        chunk_text=chunk_text,
                        chunk_index=idx,
                        qdrant_point_id=qdrant_point_id
                    )
                    db.add(book_chunk)
                    
                    # Salvar no Qdrant
                    try:
                        await qdrant_service.add_book_chunk(
                            chunk_id=qdrant_point_id,
                            text=chunk_text,
                            embedding=embedding,
                            metadata={
                                "book_id": book.id,
                                "book_title": book.title,
                                "chunk_index": idx,
                                "page_number": None
                            }
                        )
                        chunks_salvos += 1
                    except Exception as e:
                        logger.error(f"Erro ao salvar chunk {idx} no Qdrant: {e}")
                        # Continue processando outros chunks
            
            # Marcar livro como processado
            book.processed = True
            db.commit()
            
            logger.info(f"Processamento concluído para livro {book_id}: {chunks_salvos} chunks salvos")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Erro no processamento de embeddings para livro {book_id}: {e}")
        # Tentar marcar livro com erro
        try:
            from ..database import SessionLocal
            db = SessionLocal()
            try:
                book = db.query(Book).filter(Book.id == book_id).first()
                if book:
                    book.processed = False  # Manter como não processado para retry
                    db.commit()
            finally:
                db.close()
        except Exception as inner_e:
            logger.error(f"Erro ao marcar livro como não processado: {inner_e}")

@router.post("/{book_id}/process-embeddings")
async def process_embeddings_manual(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Processar embeddings manualmente usando Celery (assíncrono)"""
    try:
        # Verificar se o livro existe
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Livro não encontrado"
            )
        
        # Verificar se já existe uma task em andamento
        if book.task_id:
            try:
                result = AsyncResult(book.task_id, app=celery_app)
                if result.state in ['PENDING', 'PROGRESS']:
                    return {
                        "message": "Processamento já está em andamento",
                        "book_id": book_id,
                        "task_id": book.task_id,
                        "status": "already_processing"
                    }
            except Exception as e:
                logger.warning(f"Erro ao verificar task existente: {e}")
        
        # Verificar se temos o arquivo PDF
        if not book.file_path or not os.path.exists(book.file_path):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo PDF não encontrado"
            )
        
        # Extrair texto do PDF novamente
        with open(book.file_path, 'rb') as f:
            file_content = f.read()
        
        extraction_result = pdf_service.extract_text_from_upload(file_content)
        
        if not extraction_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao processar PDF: {extraction_result['error']}"
            )
        
        # Criar chunks do texto
        chunks = pdf_service.create_text_chunks(extraction_result["text"])
        
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não foi possível extrair texto válido do PDF"
            )
        
        # Enviar task para Celery
        task = process_pdf_embeddings.delay(book_id, chunks)
        
        # Atualizar task ID no banco
        book.task_id = task.id
        book.processed = False  # Marcar como não processado até completar
        db.commit()
        
        logger.info(f"Task de embeddings iniciada manualmente para livro {book_id}: {task.id}")
        
        return {
            "message": "Processamento de embeddings iniciado com sucesso via Celery",
            "book_id": book_id,
            "task_id": task.id,
            "status": "processing_started",
            "chunks_count": len(chunks),
            "note": f"Use GET /tasks/task/{task.id} para acompanhar o progresso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no processamento manual de embeddings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno: {str(e)}"
        )

# FUNÇÃO DESABILITADA - CAUSA TRAVAMENTO
# async def process_book_embeddings_sync(book_id: int, extraction_result: dict, db: Session):
#     """Versão síncrona SIMPLIFICADA - DESABILITADA"""
#     pass

@router.get("/test-qdrant")
async def test_qdrant_connection(current_user: User = Depends(get_current_user)):
    """Testar conexão com Qdrant via Celery"""
    try:
        # Fazer um teste simples via busca assíncrona
        task = search_similar_documents.delay("teste de conexão", limit=1)
        
        return {
            "status": "test_started",
            "message": "Teste de conexão com Qdrant iniciado via Celery",
            "task_id": task.id,
            "note": f"Use GET /tasks/task/{task.id} para ver resultado do teste"
        }
        
    except Exception as e:
        logger.error(f"Erro ao testar Qdrant: {e}")
        return {
            "status": "error",
            "message": f"Erro ao iniciar teste: {str(e)}",
            "note": "Verifique se o Celery Worker está funcionando"
        }

@router.post("/{book_id}/demo-embeddings")
async def demo_process_embeddings_endpoint(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Demonstração do sistema Celery sem dependências externas"""
    try:
        # Verificar se o livro existe
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Livro não encontrado"
            )
        
        # Simular número de chunks baseado no livro
        chunks_count = max(5, book.pages or 10)  # Mínimo 5, baseado nas páginas
        
        # Enviar task demo para Celery
        task = demo_process_embeddings.delay(book_id, chunks_count)
        
        logger.info(f"Task DEMO iniciada para livro {book_id}: {task.id}")
        
        return {
            "message": "Processamento DEMO iniciado com sucesso!",
            "book_id": book_id,
            "task_id": task.id,
            "status": "demo_started",
            "simulated_chunks": chunks_count,
            "note": f"Use GET /tasks/task/{task.id} para acompanhar (sem APIs externas)",
            "mode": "demo"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na demo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na demonstração: {str(e)}"
        )

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
        # TODO: Deletar chunks do Qdrant (DESABILITADO - causa travamento)
        # try:
        #     await qdrant_service.delete_book_chunks(book_id)
        #     logger.info(f"Chunks do Qdrant deletados para livro {book_id}")
        # except Exception as e:
        #     logger.warning(f"Erro ao deletar chunks do Qdrant: {e}")
        
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