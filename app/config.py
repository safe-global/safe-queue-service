"""
Base settings file for FastApi application.
"""

import logging.config
import os
import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict

from .loggers.safe_logger import SafeJsonFormatter


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.environ.get("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=True,
    )
    TEST: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_LEVEL_EVENTS_SERVICE: str = "INFO"
    REDIS_URL: str = "redis://"
    DATABASE_URL: str = "psql://postgres:"
    DATABASE_POOL_CLASS: str = "AsyncAdaptedQueuePool"
    DATABASE_POOL_SIZE: int = 10
    RABBITMQ_AMQP_URL: str = "amqp://guest:guest@"
    RABBITMQ_AMQP_EXCHANGE: str = "safe-transaction-service-events"
    RABBITMQ_QUEUE_EVENTS_QUEUE_NAME: str = "queue-service"
    SECRET_KEY: str = secrets.token_urlsafe(32)


settings = Settings()

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"json": {"()": SafeJsonFormatter}},  # Custom formatter class
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json",
        }
    },
    "loggers": {
        "": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console"],
            "propagate": False,
        },
        "app.services.events": {
            "level": settings.LOG_LEVEL_EVENTS_SERVICE,
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
