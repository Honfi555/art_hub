from logging import Logger

from psycopg2._psycopg import connection as pg_connection
from psycopg2.pool import SimpleConnectionPool
import psycopg2
import redis

from ..logger import configure_logs
from ..static import POSTGRES_SOURCE, REDIS_PORT, REDIS_DB, REDIS_PASSWORD, REDIS_USER, REDIS_HOST

logger: Logger = configure_logs(__name__)

POOL_MIN_CONN = 1
POOL_MAX_CONN = 2
connection_pool = SimpleConnectionPool(
    POOL_MIN_CONN,
    POOL_MAX_CONN,
    dsn=POSTGRES_SOURCE,
    connect_timeout=10
)

def connect_pg() -> pg_connection | None:
    try:
        db_connection = psycopg2.connect(
            dsn=POSTGRES_SOURCE,
            port=5432
        )
        logger.info("Подключение к PostgreSQL успешно.")
        return db_connection
    except Exception as e:
        logger.error("Ошибка подключения к PostgreSQL: %s", e)


def connect_redis() -> redis.Redis:
    """
    Подключение к Redis через пул соединений.
    Использует константы из static: REDIS_SOURCE
    """
    try:
        pool = redis.ConnectionPool(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            username=REDIS_USER,
            decode_responses=False
        )
        client = redis.Redis(connection_pool=pool)
        client.ping()
        logger.info("Подключение к Redis успешно.")
        return client
    except Exception as e:
        logger.error("Ошибка подключения к Redis: %s", e)
        raise
