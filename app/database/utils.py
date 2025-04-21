from typing import Optional
from logging import Logger

from sqlite3 import OperationalError, InterfaceError

from .connect import connect_pg
from ..logger import configure_logs

logger: Logger = configure_logs(__name__)


def check_article_owner(article_id: int, requester: str) -> Optional[bool]:
    logger.info("Проверка владельца статьи %s для пользователя %s", article_id, requester)
    conn = None
    try:
        conn = connect_pg()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT u.login
                FROM users.users u
                JOIN articles.articles a ON u.id = a.user_id
                WHERE a.article_id = %s
                """,
                (article_id,)
            )
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Статья с id={article_id} не найдена")
            actual_owner = row[0]
            if actual_owner != requester:
                raise PermissionError(
                    f"Пользователь '{requester}' не является владельцем статьи (владелец: '{actual_owner}')"
                )
        return True
    except (OperationalError, InterfaceError) as e:
        logger.error("Ошибка соединения при проверке владельца: %s", e)
        raise
    finally:
        if conn:
            conn.close()
