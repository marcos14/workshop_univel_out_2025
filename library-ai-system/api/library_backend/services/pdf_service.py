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