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
    if url.startswith("rediss://"):
        # Check if parameter already exists (case-insensitive)
        if "ssl_cert_reqs" not in url.lower():
            separator = "&" if "?" in url else "?"
            # Celery Redis backend expects uppercase CERT_NONE, CERT_OPTIONAL, or CERT_REQUIRED
            # URL encode the parameter value
            from urllib.parse import urlencode, urlparse, urlunparse, parse_qs
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            query_params["ssl_cert_reqs"] = ["CERT_NONE"]
            new_query = urlencode(query_params, doseq=True)
            new_parsed = parsed._replace(query=new_query)
            return urlunparse(new_parsed)
    return url

broker_url = fix_redis_url(settings.CELERY_BROKER_URL)
backend_url = fix_redis_url(settings.REDIS_URL)

# Log the URLs (without sensitive data) for debugging
logger.info("Redis URLs configured", 
           broker_has_ssl_cert=("ssl_cert_reqs" in broker_url.lower()),
           backend_has_ssl_cert=("ssl_cert_reqs" in backend_url.lower()))

# Create Celery app
celery_app = Celery("compile_worker")

# Configure broker and backend with SSL settings
celery_app.conf.broker_url = broker_url
celery_app.conf.result_backend = backend_url

# SSL configuration for Redis
if broker_url.startswith("rediss://"):
    celery_app.conf.broker_use_ssl = {
        "ssl_cert_reqs": "CERT_NONE",
        "ssl_ca_certs": None,
        "ssl_certfile": None,
        "ssl_keyfile": None,
    }

if backend_url.startswith("rediss://"):
    celery_app.conf.redis_backend_use_ssl = {
        "ssl_cert_reqs": "CERT_NONE",
        "ssl_ca_certs": None,
        "ssl_certfile": None,
        "ssl_keyfile": None,
    }

celery_app.conf.task_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.result_serializer = "json"
celery_app.conf.timezone = "UTC"
celery_app.conf.enable_utc = True

# Register tasks
celery_app.task(name="compile_resume")(compile_resume_task)

if __name__ == "__main__":
    celery_app.start()

