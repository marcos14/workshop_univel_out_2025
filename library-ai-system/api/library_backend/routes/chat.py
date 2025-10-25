from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ..database import get_db
from ..models import User, Conversation, Message, UserBookInteraction
from ..dto.chat_dto import (
    MessageCreate, MessageResponse, ConversationCreate, 
    ConversationResponse, ConversationWithMessages, ChatResponse
)
from ..services.openai_service import OpenAIService
from ..services.qdrant_service import QdrantService
from ..core.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Instanciar serviços
openai_service = OpenAIService()
qdrant_service = QdrantService()

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar nova conversa"""
    
    conversation = Conversation(
        user_id=current_user.id,
        title=conversation_data.title
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return ConversationResponse(**conversation.__dict__)

@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar conversas do usuário"""
    
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()
    
    result = []
    for conv in conversations:
        message_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
        conv_data = ConversationResponse(**conv.__dict__)
        conv_data.message_count = message_count
        result.append(conv_data)
    
    return result

@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter conversa com mensagens"""
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada"
        )
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    message_responses = [MessageResponse(**msg.__dict__) for msg in messages]
    
    return ConversationWithMessages(
        **conversation.__dict__,
        messages=message_responses
    )

@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
async def send_message(
    conversation_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar mensagem e obter resposta da IA"""
    
    # Verificar se conversa existe e pertence ao usuário
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada"
        )
    
    try:
        # Salvar mensagem do usuário
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=message_data.content
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)
        
        # Gerar embedding da pergunta do usuário
        query_embedding = await openai_service.generate_embedding(message_data.content)
        
        if not query_embedding:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao processar pergunta"
            )
        
        # Buscar chunks relevantes no Qdrant
        relevant_chunks = await qdrant_service.search_similar_chunks(
            query_embedding=query_embedding,
            limit=5
        )
        
        # Obter histórico da conversa
        previous_messages = db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.id != user_message.id  # Excluir a mensagem atual
        ).order_by(Message.created_at.asc()).limit(10).all()
        
        # Construir contexto de mensagens para a IA
        chat_messages = []
        for msg in previous_messages:
            chat_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Adicionar mensagem atual
        chat_messages.append({
            "role": "user",
            "content": message_data.content
        })
        
        # Gerar resposta da IA com contexto dos livros
        ai_response = await openai_service.chat_with_context(
            messages=chat_messages,
            context_chunks=relevant_chunks
        )
        
        # Extrair livros referenciados
        books_referenced = []
        context_books = []
        for chunk in relevant_chunks:
            book_title = chunk.get('book_title')
            book_id = chunk.get('book_id')
            
            if book_title and book_title not in context_books:
                context_books.append(book_title)
            
            if book_id and book_id not in books_referenced:
                books_referenced.append(book_id)
        
        # Salvar resposta da IA
        ai_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response,
            books_referenced=books_referenced if books_referenced else None
        )
        db.add(ai_message)
        
        # Atualizar timestamp da conversa
        from datetime import datetime
        conversation.updated_at = datetime.utcnow()
        
        # Registrar interações com livros
        for book_id in books_referenced:
            interaction = UserBookInteraction(
                user_id=current_user.id,
                book_id=book_id,
                interaction_type="chat_reference",
                metadata={
                    "conversation_id": conversation_id,
                    "message_id": ai_message.id,
                    "query": message_data.content
                }
            )
            db.add(interaction)
        
        db.commit()
        db.refresh(ai_message)
        
        return ChatResponse(
            conversation_id=conversation_id,
            message=MessageResponse(**ai_message.__dict__),
            context_books=context_books
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar mensagem"
        )

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletar conversa"""
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada"
        )
    
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversa deletada com sucesso"}