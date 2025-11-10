"""Celery worker entry point"""

import structlog
from celery import Celery
from worker.config import settings
from worker.tasks.compile import compile_resume_task

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Fix Redis URLs for SSL (Upstash requires ssl_cert_reqs parameter)
def fix_redis_url(url: str) -> str:
    """Add ssl_cert_reqs parameter to rediss:// URLs if missing"""
    if url.startswith("rediss://") and "ssl_cert_reqs" not in url:
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}ssl_cert_reqs=none"
    return url

broker_url = fix_redis_url(settings.CELERY_BROKER_URL)
backend_url = fix_redis_url(settings.REDIS_URL)

# Create Celery app
celery_app = Celery(
    "compile_worker",
    broker=broker_url,
    backend=backend_url,
)

celery_app.conf.task_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.result_serializer = "json"
celery_app.conf.timezone = "UTC"
celery_app.conf.enable_utc = True

# Register tasks
celery_app.task(name="compile_resume")(compile_resume_task)

if __name__ == "__main__":
    celery_app.start()

