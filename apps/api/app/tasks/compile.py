"""PDF compilation tasks using Celery"""

from celery import Celery
from app.config import settings

celery_app = Celery(
    "compile_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.task_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.result_serializer = "json"
celery_app.conf.timezone = "UTC"
celery_app.conf.enable_utc = True


@celery_app.task(name="compile_resume")
def compile_resume_task(variant_id: str):
    """
    Compile resume variant to PDF using Tectonic in Docker.
    
    This task will be handled by the worker service.
    """
    # This will be implemented in the worker service
    # The API just triggers the task
    from uuid import UUID
    
    # Update database with compilation status
    # Actual compilation happens in worker
    return {
        "variant_id": variant_id,
        "status": "queued",
        "message": "Compilation task queued",
    }

