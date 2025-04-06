from typing import Optional
from logging import Logger

from psycopg2.errors import OperationalError, InterfaceError

from .connect import connect
from ..logger import configure_logs
from ..models.articles import ArticleData, ArticleAnnouncement

logger: Logger = configure_logs(__name__)


def select_articles_announcement(login: Optional[str] = None) -> list[ArticleAnnouncement]:
	logger.info("Начало получения статей из базы данных.")
	conn = None
	try:
		conn = connect()
		with conn.cursor() as cur:
			query = """
                SELECT 
                    art.article_id,
                    art.tittle,
                    us.login,
                    art.announcement
                FROM articles.articles art
                JOIN users.users us ON art.user_id = us.id
            """
			params = []
			if login:
				query += " WHERE us.login = %s"
				params.append(login)
			cur.execute(query, params)
			result = cur.fetchall()
			logger.info("Количество полученных статей %s", len(result))
			return result
	except (OperationalError, InterfaceError) as e:
		logger.error("Ошибка соединения: %s", e)
		raise
	except Exception as e:
		logger.error("Ошибка при выполнении запроса: %s", e)
		raise
	finally:
		if conn:
			conn.close()


def select_article(article_id: int) -> ArticleData:
	logger.info("Начало получения статьи, c id %s", article_id)
	conn = None
	try:
		conn = connect()
		with conn.cursor() as cur:
			query = """
                SELECT 
					art.article_id,
					art.tittle,
					us.login,
					art.article_body
                FROM articles.articles art
                JOIN users.users us ON art.user_id = us.id
                WHERE article_id = %s
            """
			cur.execute(query, (article_id,))
			result = cur.fetchone()
			logger.info("Получена статься с id %s", article_id)
			return result
	except (OperationalError, InterfaceError) as e:
		logger.error("Ошибка соединения: %s", e)
		raise
	except Exception as e:
		logger.error("Ошибка при выполнении запроса: %s", e)
		raise
	finally:
		if conn:
			conn.close()


def select_article_images(article_id: int, max_amount: Optional[int]) -> list[tuple[bytes]]:
	logger.info("Начало получения фото к статье, c id %s", article_id)
	conn = None
	try:
		conn = connect()
		with conn.cursor() as cur:
			query = """
                SELECT 
                    image
                FROM articles.images
                WHERE article_id = %s
            """
			params = [article_id]
			if max_amount:
				query += " LIMIT %s"
				params.append(max_amount)
			cur.execute(query, params)
			result = cur.fetchall()
			logger.info("Получены фото к статье с id %s", article_id)
			return result
	except (OperationalError, InterfaceError) as e:
		logger.error("Ошибка соединения: %s", e)
		raise
	except Exception as e:
		logger.error("Ошибка при выполнении запроса: %s", e)
		raise
	finally:
		if conn:
			conn.close()


def insert_articles(articles: list[ArticleData]) -> None:
	logger.info("Начало вставки статей в количестве %s", len(articles))
	conn = None
	try:
		conn = connect()
		with conn.cursor() as cur:
			query = """
                INSERT INTO articles.articles
                (tittle, user_id, article_body) 
                VALUES (%s, %s, %s)
            """
			data = [(article.title, article.user_id, article.article_body) for article in articles]
			cur.executemany(query, data)
			conn.commit()
			logger.info("Количество вставленных статей %s", len(articles))
	except (OperationalError, InterfaceError) as e:
		logger.error("Ошибка соединения: %s", e)
		raise
	except Exception as e:
		logger.error("Ошибка при выполнении запроса: %s", e)
		raise
	finally:
		if conn:
			conn.close()


def delete_articles(article_id: int) -> None:
	logger.info("Начало удаления статьи %s", article_id)
	conn = None
	try:
		conn = connect()
		with conn.cursor() as cur:
			query = """
                DELETE FROM articles.articles
                WHERE article_id = %s
            """
			cur.execute(query, (article_id,))
			conn.commit()
			logger.info("Удалена статья %s", article_id)
	except (OperationalError, InterfaceError) as e:
		logger.error("Ошибка соединения: %s", e)
		raise
	except Exception as e:
		logger.error("Ошибка при выполнении запроса: %s", e)
		raise
	finally:
		if conn:
			conn.close()
