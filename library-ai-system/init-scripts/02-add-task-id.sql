-- Migração para adicionar coluna task_id na tabela books
-- Data: 2024-10-24
-- Versão: v1.1.0 - Implementação Redis + Celery

-- Adicionar coluna task_id para tracking de tasks do Celery
ALTER TABLE books ADD COLUMN IF NOT EXISTS task_id VARCHAR(255);

-- Criar índice para melhor performance em consultas por task_id
CREATE INDEX IF NOT EXISTS idx_books_task_id ON books(task_id);

-- Comentário para documentação
COMMENT ON COLUMN books.task_id IS 'ID da task do Celery para tracking de processamento de embeddings';