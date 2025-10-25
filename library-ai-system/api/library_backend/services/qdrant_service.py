from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client.http.exceptions import UnexpectedResponse
import os
import logging
from typing import List, Dict, Any, Optional
import uuid

logger = logging.getLogger(__name__)

class QdrantService:
    def __init__(self):
        self.client = None
        self.collection_name = "library_books"
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self._initialized = False
        
    def _ensure_initialized(self):
        """Garantir que o cliente está inicializado"""
        if not self._initialized:
            try:
                self.client = QdrantClient(url=self.qdrant_url)
                self._initialized = True
                logger.info(f"Qdrant cliente inicializado: {self.qdrant_url}")
                
                # Verificar se a collection existe, se não, criar
                try:
                    collection_info = self.client.get_collection(self.collection_name)
                    logger.info(f"Collection '{self.collection_name}' já existe")
                except UnexpectedResponse:
                    # Collection não existe, criar
                    self.client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(
                            size=1536,  # Dimensão dos embeddings OpenAI text-embedding-ada-002
                            distance=Distance.COSINE
                        )
                    )
                    logger.info(f"Collection '{self.collection_name}' criada com sucesso")
                    
            except Exception as e:
                logger.error(f"Erro ao inicializar Qdrant: {e}")
                self.client = None
                self._initialized = False
        
    async def initialize(self):
        """Inicializar conexão com Qdrant e criar collection se necessário"""
        try:
            self.client = QdrantClient(url=self.qdrant_url)
            
            # Verificar se a collection existe, se não, criar
            try:
                collection_info = self.client.get_collection(self.collection_name)
                logger.info(f"Collection '{self.collection_name}' já existe")
            except UnexpectedResponse:
                # Collection não existe, criar
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=1536,  # Dimensão dos embeddings OpenAI text-embedding-ada-002
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Collection '{self.collection_name}' criada com sucesso")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar Qdrant: {e}")
            raise
    
    async def add_book_chunk(self, chunk_id: str, text: str, embedding: List[float], metadata: Dict[str, Any]) -> bool:
        """Adicionar chunk de livro ao Qdrant"""
        try:
            # Garantir que está inicializado
            self._ensure_initialized()
            
            if not self.client:
                logger.error("Cliente Qdrant não inicializado")
                return False
                
            point = PointStruct(
                id=chunk_id,
                vector=embedding,
                payload={
                    "text": text,
                    "book_id": metadata.get("book_id"),
                    "book_title": metadata.get("book_title"),
                    "chunk_index": metadata.get("chunk_index"),
                    "page_number": metadata.get("page_number"),
                }
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"Chunk {chunk_id} adicionado ao Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar chunk ao Qdrant: {e}")
            return False
    
    async def search_similar_chunks(self, query_embedding: List[float], book_ids: Optional[List[int]] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Buscar chunks similares baseado no embedding da query"""
        try:
            # Garantir que está inicializado
            self._ensure_initialized()
            
            if not self.client:
                logger.error("Cliente Qdrant não inicializado")
                return []
            
            # Criar filtro se book_ids foram especificados
            query_filter = None
            if book_ids:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="book_id",
                            match=MatchValue(value=book_id)
                        ) for book_id in book_ids
                    ]
                )
            
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=limit,
                with_payload=True
            )
            
            results = []
            for hit in search_result:
                results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "text": hit.payload.get("text"),
                    "book_id": hit.payload.get("book_id"),
                    "book_title": hit.payload.get("book_title"),
                    "chunk_index": hit.payload.get("chunk_index"),
                    "page_number": hit.payload.get("page_number"),
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Erro ao buscar chunks similares: {e}")
            return []
    
    async def delete_book_chunks(self, book_id: int) -> bool:
        """Deletar todos os chunks de um livro específico"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="book_id",
                            match=MatchValue(value=book_id)
                        )
                    ]
                )
            )
            
            logger.info(f"Chunks do livro {book_id} deletados do Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao deletar chunks do livro {book_id}: {e}")
            return False
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Obter informações da collection"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "points_count": info.points_count,
                "status": info.status,
                "vectors_count": info.vectors_count
            }
        except Exception as e:
            logger.error(f"Erro ao obter informações da collection: {e}")
            return {}