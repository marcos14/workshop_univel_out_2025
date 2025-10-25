from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import hashlib
import secrets
from datetime import datetime, timedelta
import jwt
import os
from typing import Optional

from ..database import get_db
from ..models import User

# Configurações
SECRET_KEY = os.getenv("SECRET_KEY", "library_secret_key_2024")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Bearer token
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar senha usando PBKDF2"""
    try:
        # Extrair salt e hash do formato: salt$hash
        parts = hashed_password.split('$')
        if len(parts) != 2:
            return False
        
        salt, stored_hash = parts
        # Gerar hash da senha fornecida com o mesmo salt
        password_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), 
                                           bytes.fromhex(salt), 100000)
        return password_hash.hex() == stored_hash
    except:
        return False

def get_password_hash(password: str) -> str:
    """Gerar hash da senha usando PBKDF2"""
    # Gerar salt aleatório
    salt = secrets.token_hex(32)
    # Gerar hash da senha
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), 
                                       bytes.fromhex(salt), 100000)
    # Retornar no formato: salt$hash
    return f"{salt}${password_hash.hex()}"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Criar token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verificar e decodificar token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Obter usuário atual baseado no token"""
    
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def authenticate_user(email: str, password: str, db: Session) -> Optional[User]:
    """Autenticar usuário"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user