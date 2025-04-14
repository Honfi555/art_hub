import base64
from typing import Optional
from logging import Logger

from psycopg2.errors import OperationalError, InterfaceError

from .connect import connect
from ..logger import configure_logs
from ..models.articles import ImagesAdd

__all__: list[str] = ["delete_images", "insert_images", "select_article_images"]
logger: Logger = configure_logs(__name__)


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
