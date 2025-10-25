from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from celery.result import AsyncResult
from typing import Dict, Any

from ..database import get_db
from ..models import Book, User
from ..core.auth import get_current_user
from ..celery_app import celery_app
from ..tasks.embeddings_tasks import search_similar_documents

router = APIRouter()

@router.get("/task/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Verificar status de uma task do Celery"""
    try:
        result = AsyncResult(task_id, app=celery_app)
        
        if result.state == 'PENDING':
            response = {
                'state': result.state,
                'status': 'Task está pendente...'
            }
        elif result.state == 'PROGRESS':
            response = {
                'state': result.state,
                'current': result.info.get('current', 0),
                'total': result.info.get('total', 1),
                'status': result.info.get('status', '')
            }
        elif result.state == 'SUCCESS':
            response = {
                'state': result.state,
                'result': result.result
            }
        else:  # FAILURE
            response = {
                'state': result.state,
                'error': str(result.info)
            }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao verificar status da task: {str(e)}"
        )

@router.get("/book/{book_id}/processing-status")
async def get_book_processing_status(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verificar status de processamento de um livro"""
    book = db.query(Book).filter(Book.id == book_id).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Livro não encontrado"
        )
    
    if not book.task_id:
        return {
            'book_id': book_id,
            'processed': book.processed,
            'status': 'completed' if book.processed else 'no_task'
        }
    
    try:
        result = AsyncResult(book.task_id, app=celery_app)
        
        response = {
            'book_id': book_id,
            'task_id': book.task_id,
            'processed': book.processed,
            'task_state': result.state
        }
        
        if result.state == 'PROGRESS':
            response.update({
                'current': result.info.get('current', 0),
                'total': result.info.get('total', 1),
                'status': result.info.get('status', '')
            })
        elif result.state == 'SUCCESS':
            # Atualizar status do livro se a task foi concluída
            if not book.processed:
                book.processed = True
                db.commit()
            response['result'] = result.result
        elif result.state == 'FAILURE':
            response['error'] = str(result.info)
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao verificar status: {str(e)}"
        )

@router.post("/search-embeddings")
async def search_with_embeddings(
    query: str,
    limit: int = 5,
    current_user: User = Depends(get_current_user)
):
    """Buscar documentos usando embeddings via Celery"""
    try:
        # Enviar task de busca para Celery
        task = search_similar_documents.delay(query, limit=limit)
        
        return {
            'message': 'Busca iniciada',
            'task_id': task.id,
            'query': query
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao iniciar busca: {str(e)}"
        )