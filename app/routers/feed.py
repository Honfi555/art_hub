import base64
from typing import Optional
from logging import Logger

from fastapi import APIRouter, Header, status, HTTPException
from fastapi.responses import JSONResponse

from ..logger import configure_logs
from ..dependecies import verify_jwt, get_jwt_login
from ..models import ImagesAdd
from ..models.articles import ArticleData, ArticleAnnouncement, ArticleFull, ArticleAdd
from ..database.articles import (insert_images, select_articles_announcement, select_article, insert_article,
								 delete_article,
								 select_article_images, select_article_full, update_article, delete_images)

feed_router: APIRouter = APIRouter(
	prefix="/feed",
	tags=["Маршруты для получения статей пользователей"]
)
logger: Logger = configure_logs(__name__)


@feed_router.get("/articles")
@verify_jwt
async def get_articles(authorization: str = Header(...),
					   amount: Optional[int] = 10,
					   chunk: Optional[int] = 1,
					   login: Optional[str] = None):
	try:
		articles_data: list[ArticleAnnouncement] = select_articles_announcement(amount, chunk, login)
		return JSONResponse(status_code=status.HTTP_200_OK, content={"articles": articles_data})
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@feed_router.get("/article")
@verify_jwt
async def get_article(article_id: int, authorization: str = Header(...)):
	try:
		article_data: ArticleData = select_article(article_id)
		return JSONResponse(status_code=status.HTTP_200_OK, content={"article": article_data})
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@feed_router.get("/article_full")
@verify_jwt
async def get_article(article_id: int, authorization: str = Header(...)):
	try:
		article_data: ArticleFull = select_article_full(article_id)
		return JSONResponse(status_code=status.HTTP_200_OK, content={"article": article_data})
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@feed_router.get("/article_images")
@verify_jwt
async def get_article_images(article_id: int,  authorization: str = Header(...), max_amount: Optional[int] = None):
	try:
		article_images: list[tuple[int, bytes]] = select_article_images(article_id, max_amount)
		# Преобразуем список байтов в список Base64-строк
		encoded_images = [(image_id, base64.b64encode(img).decode("utf-8")) for (image_id, img) in article_images]

		return JSONResponse(
			status_code=status.HTTP_200_OK,
			content={"images": encoded_images}
		)
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@feed_router.delete("/remove_images")
@verify_jwt
async def remove_article_images(image_ids: list[int], authorization: str = Header(...)):
	try:
		delete_images(image_ids)
		return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "success"})
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@feed_router.put("/add_images")
@verify_jwt
async def add_article_images(images_data: ImagesAdd, authorization: str = Header(...)):
	try:
		insert_images(images_data)
		return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "success"})
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@feed_router.post("/add_article")
@verify_jwt
async def add_article(article_data: ArticleAdd, authorization: str = Header(...)):
	try:
		login: str = get_jwt_login(authorization)
		article_id: int = insert_article(
				ArticleFull(id=0,
							title=article_data.title,
							user_name=login,
							announcement=article_data.announcement,
							article_body=article_data.article_body)
		)
		return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "success", "article_id": article_id})
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@feed_router.put("/update_article")
@verify_jwt
async def add_article(article_data: ArticleData, authorization: str = Header(...)):
	try:
		update_article(article_data)
		return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "success"})
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@feed_router.delete("/remove_article")
@verify_jwt
async def remove_article(article_id: int, authorization: str = Header(...)):
	try:
		delete_article(article_id)
		return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "success"})
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
