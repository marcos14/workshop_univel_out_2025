from celery import current_task
from library_backend.celery_app import celery_app
from openai import OpenAI
import os
import time
from typing import List, Dict
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_HOST = os.getenv("QDRANT_HOST", "library-qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

# Inicializar cliente OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

@celery_app.task(bind=True)
def process_pdf_embeddings(self, book_id: int, text_chunks: List[str], collection_name: str = "library_books"):
    """
    Task para processar embeddings de um PDF de forma assíncrona
    """
    try:
        logger.info(f"Iniciando processamento de embeddings para livro {book_id}")
        
        # Verificar se temos OpenAI API Key
        if not OPENAI_API_KEY or not openai_client:
            logger.warning("OPENAI_API_KEY não configurada, executando em modo simulação")
            return process_pdf_embeddings_simulation(self, book_id, text_chunks, collection_name)
        
        # Atualizar status da task
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': len(text_chunks), 'status': 'Conectando ao Qdrant...'}
        )
        
        # Conectar ao Qdrant
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # Verificar se a collection existe, senão criar
        try:
            client.get_collection(collection_name)
            logger.info(f"Collection {collection_name} já existe")
        except Exception:
            logger.info(f"Criando collection {collection_name}")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
        
        # Processar embeddings em lotes
        batch_size = 5
        total_processed = 0
        points = []
        
        for i in range(0, len(text_chunks), batch_size):
            batch = text_chunks[i:i + batch_size]
            
            # Gerar embeddings para o lote
            for chunk_idx, chunk in enumerate(batch):
                try:
                    response = openai_client.embeddings.create(
                        input=chunk,
                        model="text-embedding-ada-002"
                    )
                    
                    embedding = response.data[0].embedding
                    
                    # Criar point para Qdrant
                    point = PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={
                            "book_id": book_id,
                            "chunk_index": i + chunk_idx,
                            "text": chunk,
                            "chunk_size": len(chunk)
                        }
                    )
                    points.append(point)
                    
                    total_processed += 1
                    
                    # Atualizar progress
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current': total_processed,
                            'total': len(text_chunks),
                            'status': f'Processado {total_processed}/{len(text_chunks)} chunks'
                        }
                    )
                    
                    # Pequena pausa entre requisições
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Erro ao processar chunk {i + chunk_idx}: {str(e)}")
                    continue
            
            # Inserir lote no Qdrant
            if points:
                try:
                    client.upsert(
                        collection_name=collection_name,
                        points=points
                    )
                    logger.info(f"Inserido lote de {len(points)} pontos no Qdrant")
                    points = []  # Limpar lote
                except Exception as e:
                    logger.error(f"Erro ao inserir no Qdrant: {str(e)}")
            
            # Pausa entre lotes
            time.sleep(1)
        
        logger.info(f"Processamento concluído para livro {book_id}")
        
        return {
            'status': 'completed',
            'book_id': book_id,
            'chunks_processed': total_processed,
            'collection': collection_name,
            'mode': 'real'
        }
        
    except Exception as e:
        logger.error(f"Erro no processamento de embeddings: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'book_id': book_id}
        )
        raise

def process_pdf_embeddings_simulation(task_self, book_id: int, text_chunks: List[str], collection_name: str):
    """
    Simulação do processamento quando não temos API keys configuradas
    """
    logger.info(f"Executando SIMULAÇÃO de embeddings para livro {book_id}")
    
    total_chunks = len(text_chunks)
    
    for i in range(total_chunks):
        # Simular processamento
        time.sleep(1)  # 1 segundo por chunk
        
        # Atualizar progress
        task_self.update_state(
            state='PROGRESS',
            meta={
                'current': i + 1,
                'total': total_chunks,
                'status': f'Simulando chunk {i + 1}/{total_chunks}',
                'mode': 'simulation'
            }
        )
        
        logger.info(f"SIMULAÇÃO: Chunk {i + 1}/{total_chunks} processado")
    
    return {
        'status': 'completed',
        'book_id': book_id,
        'chunks_processed': total_chunks,
        'collection': collection_name,
        'mode': 'simulation',
        'message': 'Processamento simulado concluído! Configure OPENAI_API_KEY para processamento real.'
    }

@celery_app.task(bind=True)
def search_similar_documents(self, query: str, collection_name: str = "library_books", limit: int = 5):
    """
    Task para buscar documentos similares usando embeddings
    """
    try:
        logger.info(f"Buscando documentos similares para: {query}")
        
        # Verificar se temos OpenAI configurado
        if not OPENAI_API_KEY or not openai_client:
            logger.warning("OPENAI_API_KEY não configurada, retornando resultados simulados")
            return {
                'status': 'completed',
                'query': query,
                'results': [],
                'mode': 'simulation',
                'message': 'Configure OPENAI_API_KEY para busca real'
            }
        
        # Gerar embedding da query
        response = openai_client.embeddings.create(
            input=query,
            model="text-embedding-ada-002"
        )
        
        query_embedding = response.data[0].embedding
        
        # Conectar ao Qdrant
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # Fazer busca
        search_result = client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit,
            with_payload=True
        )
        
        # Formatar resultados
        results = []
        for hit in search_result:
            results.append({
                'book_id': hit.payload['book_id'],
                'text': hit.payload['text'],
                'score': hit.score,
                'chunk_index': hit.payload['chunk_index']
            })
        
        return {
            'status': 'completed',
            'query': query,
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Erro na busca: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'query': query}
        )
        raise

@celery_app.task
def cleanup_book_embeddings(book_id: int, collection_name: str = "library_books"):
    """
    Task para limpar embeddings de um livro específico
    """
    try:
        logger.info(f"Limpando embeddings do livro {book_id}")
        
        # Conectar ao Qdrant
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # Deletar pontos do livro
        client.delete(
            collection_name=collection_name,
            points_selector={"filter": {"must": [{"key": "book_id", "match": {"value": book_id}}]}}
        )
        
        logger.info(f"Embeddings do livro {book_id} removidos com sucesso")
        
        return {
            'status': 'completed',
            'book_id': book_id,
            'action': 'deleted'
        }
        
    except Exception as e:
        logger.error(f"Erro ao limpar embeddings: {str(e)}")
        raise