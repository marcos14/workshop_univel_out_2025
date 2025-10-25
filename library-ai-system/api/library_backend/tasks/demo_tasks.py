# Teste manual do sistema Celery - Versão Demo
# Para verificar se o sistema está funcionando sem depender de APIs externas

from library_backend.celery_app import celery_app
import time
from typing import List
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def demo_process_embeddings(self, book_id: int, chunks_count: int):
    """
    Task de demonstração que simula o processamento de embeddings
    sem depender de APIs externas (OpenAI/Qdrant)
    """
    try:
        logger.info(f"Iniciando processamento DEMO para livro {book_id}")
        
        # Simular processamento de chunks
        total_chunks = chunks_count
        
        for i in range(total_chunks):
            # Simular processamento de um chunk
            time.sleep(2)  # 2 segundos por chunk para simular trabalho
            
            # Atualizar progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': i + 1,
                    'total': total_chunks,
                    'status': f'Processando chunk {i + 1}/{total_chunks} (DEMO)',
                    'chunk_processed': f'Chunk {i + 1} simulado com sucesso'
                }
            )
            
            logger.info(f"DEMO: Chunk {i + 1}/{total_chunks} processado")
        
        logger.info(f"Processamento DEMO concluído para livro {book_id}")
        
        return {
            'status': 'completed',
            'book_id': book_id,
            'chunks_processed': total_chunks,
            'mode': 'demo',
            'message': 'Processamento DEMO concluído com sucesso!',
            'note': 'Esta foi uma simulação. Para processamento real, configure OPENAI_API_KEY'
        }
        
    except Exception as e:
        logger.error(f"Erro no processamento DEMO: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'book_id': book_id, 'mode': 'demo'}
        )
        raise