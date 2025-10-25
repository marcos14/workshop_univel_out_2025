from celery import Celery
import os

# Configuração do Celery
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Criar instância do Celery
celery_app = Celery(
    "library_backend",
    broker=redis_url,
    backend=redis_url,
    include=[
        "library_backend.tasks.embeddings_tasks",
        "library_backend.tasks.demo_tasks"
    ]
)

# Configurações do Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos limite por task
    task_soft_time_limit=25 * 60,  # 25 minutos soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)