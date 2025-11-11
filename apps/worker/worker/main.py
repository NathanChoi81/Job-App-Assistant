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

# Remove ssl_cert_reqs from URLs if present (Redis client doesn't accept it in URL)
# SSL will be configured through Celery's connection options instead
def clean_redis_url(url: str) -> str:
    """Remove ssl_cert_reqs parameter from URL if present"""
    if "ssl_cert_reqs" in url.lower():
        from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        # Remove ssl_cert_reqs from query params
        query_params.pop("ssl_cert_reqs", None)
        query_params.pop("SSL_CERT_REQS", None)
        new_query = urlencode(query_params, doseq=True)
        new_parsed = parsed._replace(query=new_query)
        return urlunparse(new_parsed)
    return url

# Clean URLs (remove ssl_cert_reqs if present)
broker_url = clean_redis_url(settings.CELERY_BROKER_URL)
backend_url = clean_redis_url(settings.REDIS_URL)

logger.info("Redis URLs configured",
           broker_scheme=broker_url.split("://")[0] if "://" in broker_url else "unknown",
           backend_scheme=backend_url.split("://")[0] if "://" in backend_url else "unknown")

# Create Celery app
celery_app = Celery(
    "compile_worker",
    broker=broker_url,
    backend=backend_url,
)

# SSL configuration for Redis (Upstash requires SSL but doesn't verify certificates)
# Configure SSL through Celery settings, not URL parameters
if broker_url.startswith("rediss://"):
    # Use ssl_cert_reqs as integer constant (0 = CERT_NONE)
    # redis-py expects ssl_cert_reqs as ssl.SSLContext.verify_mode value
    import ssl
    celery_app.conf.broker_use_ssl = {
        "ssl_cert_reqs": ssl.CERT_NONE,
        "ssl_ca_certs": None,
        "ssl_certfile": None,
        "ssl_keyfile": None,
    }

if backend_url.startswith("rediss://"):
    import ssl
    celery_app.conf.redis_backend_use_ssl = {
        "ssl_cert_reqs": ssl.CERT_NONE,
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

