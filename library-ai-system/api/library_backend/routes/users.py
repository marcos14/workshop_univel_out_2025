from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..dto.user_dto import UserResponse
from ..core.auth import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Obter informações do usuário logado"""
    return UserResponse(**current_user.__dict__)