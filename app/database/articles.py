from typing import Optional
from logging import Logger

from psycopg2.errors import OperationalError, InterfaceError

from .connect import connect
from ..logger import configure_logs
from ..models.articles import ArticleData, ArticleAnnouncement, ArticleFull

__all__: list[str] = ["select_articles_announcement", "select_article", "select_article_full", "insert_article",
					  "update_article", "delete_article"]
logger: Logger = configure_logs(__name__)


def select_articles_announcement(amount: Optional[int] = None,
								 chunk: Optional[int] = None,
								 login: Optional[str] = None) -> list[ArticleAnnouncement]:
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
				query += "WHERE us.login = %s"
				params.append(login)
			query += "ORDER BY art.article_id DESC"
			if amount and chunk:
				query += """
				OFFSET %s
				LIMIT %s
				"""
				params.extend([(chunk - 1) * amount, amount])
			logger.info(query)
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


def select_article_full(article_id: int) -> ArticleFull:
	logger.info("Начало получения полной статьи, c id %s", article_id)
	conn = None
	try:
		conn = connect()
		with conn.cursor() as cur:
			query = """
				SELECT 
					art.article_id,
					art.tittle,
					us.login,
					art.announcement,
					art.article_body
				FROM articles.articles art
				JOIN users.users us ON art.user_id = us.id
				WHERE article_id = %s
			"""
			cur.execute(query, (article_id,))
			result = cur.fetchone()
			logger.info("Получена полная статься, с id %s", article_id)
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


def insert_article(article: ArticleFull) -> int:
	logger.info("Начало вставки статьи, с названием %s", article.title)
	conn = None
	try:
		conn = connect()
		with conn.cursor() as cur:
			query = """
					INSERT INTO articles.articles
					(tittle, user_id, announcement, article_body)
					VALUES
					(%s, (SELECT id FROM users.users WHERE login = %s), %s, %s)
					RETURNING article_id;
			"""
			data = (article.title, article.user_name, article.announcement, article.article_body)
			cur.execute(query, data)
			result = cur.fetchone()[0]
			conn.commit()
			logger.info("Вставлена статься, с названием %s", article.title)
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


def update_article(article: ArticleData) -> None:
	logger.info("Начало обновления статьи, с id %s", article.id)
	conn = None
	try:
		conn = connect()
		with conn.cursor() as cur:
			query = """
				UPDATE articles.articles 
				SET tittle = %s, article_body = %s, announcement = %s
				WHERE article_id = %s
			"""
			data = (article.title, article.article_body, article.announcement, article.id)
			cur.executemany(query, data)
			conn.commit()
			logger.info("Обновлена статья, с id %s", article.id)
	except (OperationalError, InterfaceError) as e:
		logger.error("Ошибка соединения: %s", e)
		raise
	except Exception as e:
		logger.error("Ошибка при выполнении запроса: %s", e)
		raise
	finally:
		if conn:
			conn.close()


def delete_article(article_id: int) -> None:
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
