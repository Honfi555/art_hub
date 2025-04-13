import base64
from typing import Optional
from logging import Logger

from psycopg2.errors import OperationalError, InterfaceError

from .connect import connect
from ..logger import configure_logs
from ..models import ImagesAdd
from ..models.articles import ArticleData, ArticleAnnouncement, ArticleFull

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
				query += "WHERE us.login = %s"
				params.append(login)
			query += "ORDER BY art.article_id DESC"
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


def select_article_images(article_id: int, max_amount: Optional[int]) -> list[tuple[int, bytes]]:
	logger.info("Начало получения фото к статье, c id %s", article_id)
	conn = None
	try:
		conn = connect()
		with conn.cursor() as cur:
			query = """
				SELECT
					id,
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


def insert_images(images_data: ImagesAdd) -> None:
	logger.info("Начало вставки изображений к статье, с id %s", images_data.article_id)
	conn = None
	try:
		conn = connect()
		with conn.cursor() as cur:
			query = """
				INSERT INTO articles.images
					(image, article_id)
				VALUES
					(%s, %s)
			"""
			# Декодирование base64-строк в байты
			data = [(base64.b64decode(image), images_data.article_id) for image in images_data.images]
			cur.executemany(query, data)
			conn.commit()
			logger.info("Вставлены фото для статьи, с id %s", images_data.article_id)
	except (OperationalError, InterfaceError) as e:
		logger.error("Ошибка соединения: %s", e)
		raise
	except Exception as e:
		logger.error("Ошибка при выполнении запроса: %s", e)
		raise
	finally:
		if conn:
			conn.close()


def delete_images(images_ids: list[int]) -> None:
	logger.info("Начало удаления фото, в количестве %s", len(images_ids))
	conn = None
	try:
		conn = connect()
		with conn.cursor() as cur:
			query = """
				DELETE FROM articles.images
				WHERE article_id in %s
			"""
			cur.execute(query, (images_ids,))
			conn.commit()
			logger.info("Удалены фото, в количестве %s", len(images_ids))
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
