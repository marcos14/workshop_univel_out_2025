import PyPDF2
import io
import logging
from typing import List, Dict, Any
import os

logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extrair texto de um arquivo PDF"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                text_content = ""
                pages_content = []
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text_content += page_text + "\n"
                    pages_content.append({
                        "page_number": page_num + 1,
                        "text": page_text
                    })
                
                metadata = {}
                if pdf_reader.metadata:
                    metadata = {
                        "title": pdf_reader.metadata.get("/Title", ""),
                        "author": pdf_reader.metadata.get("/Author", ""),
                        "subject": pdf_reader.metadata.get("/Subject", ""),
                        "creator": pdf_reader.metadata.get("/Creator", ""),
                        "producer": pdf_reader.metadata.get("/Producer", ""),
                        "creation_date": pdf_reader.metadata.get("/CreationDate", ""),
                        "modification_date": pdf_reader.metadata.get("/ModDate", "")
                    }
                
                return {
                    "success": True,
                    "text": text_content,
                    "pages": pages_content,
                    "total_pages": len(pdf_reader.pages),
                    "metadata": metadata
                }
                
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "pages": [],
                "total_pages": 0,
                "metadata": {}
            }
    
    def extract_text_from_upload(self, file_content: bytes) -> Dict[str, Any]:
        """Extrair texto de um arquivo PDF em memória"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            
            text_content = ""
            pages_content = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text_content += page_text + "\n"
                pages_content.append({
                    "page_number": page_num + 1,
                    "text": page_text
                })
            
            metadata = {}
            if pdf_reader.metadata:
                metadata = {
                    "title": pdf_reader.metadata.get("/Title", ""),
                    "author": pdf_reader.metadata.get("/Author", ""),
                    "subject": pdf_reader.metadata.get("/Subject", ""),
                    "creator": pdf_reader.metadata.get("/Creator", ""),
                    "producer": pdf_reader.metadata.get("/Producer", ""),
                    "creation_date": pdf_reader.metadata.get("/CreationDate", ""),
                    "modification_date": pdf_reader.metadata.get("/ModDate", "")
                }
            
            return {
                "success": True,
                "text": text_content,
                "pages": pages_content,
                "total_pages": len(pdf_reader.pages),
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF em memória: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "pages": [],
                "total_pages": 0,
                "metadata": {}
            }
    
    def validate_pdf_file(self, file_content: bytes) -> bool:
        """Validar se o arquivo é um PDF válido"""
        try:
            PyPDF2.PdfReader(io.BytesIO(file_content))
            return True
        except Exception:
            return False
    
    def create_text_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Criar chunks de texto para processamento de embeddings"""
        if not text or not text.strip():
            return []
        
        # Limpar o texto
        text = text.strip()
        
        # Se o texto é menor que o chunk_size, retornar como um único chunk
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Calcular o fim do chunk
            end = start + chunk_size
            
            # Se não é o último chunk, tentar quebrar em uma palavra
            if end < len(text):
                # Procurar por quebra de linha ou espaço para quebrar o texto
                for i in range(end, max(start + chunk_size - 200, start), -1):
                    if text[i] in ['\n', '.', '!', '?']:
                        end = i + 1
                        break
                    elif text[i] == ' ':
                        end = i
                        break
            
            # Extrair o chunk
            chunk = text[start:end].strip()
            
            if chunk:  # Só adicionar chunks não vazios
                chunks.append(chunk)
            
            # Calcular próximo início com overlap
            start = max(start + 1, end - overlap)
            
            # Evitar loop infinito
            if start >= len(text):
                break
        
        logger.info(f"Texto dividido em {len(chunks)} chunks")
        return chunks