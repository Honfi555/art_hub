from logging import Logger

import psycopg2
from psycopg2._psycopg import connection
from psycopg2.pool import SimpleConnectionPool

from ..logger import configure_logs
from ..static import DATA_SOURCE

logger: Logger = configure_logs(__name__)

# Настройка пула соединений
POOL_MIN_CONN = 1
POOL_MAX_CONN = 2
connection_pool = SimpleConnectionPool(
    POOL_MIN_CONN,
    POOL_MAX_CONN,
    dsn=DATA_SOURCE,
    connect_timeout=10
)


def connect() -> connection | None:
    try:
        db_connection: psycopg2.extensions.connection = psycopg2.connect(
            dsn=DATA_SOURCE,
            port=5432
        )
        logger.info("Подключение к базе данных успешно.")
        return db_connection
    except Exception as e:
        logger.error("Ошибка подключения к базе данных: %s", e)
