import base64
from typing import Optional
from logging import Logger

from fastapi import APIRouter, Header, status, HTTPException
from fastapi.responses import JSONResponse

from ..logger import configure_logs
from ..dependecies import verify_jwt
from ..models.articles import ArticleData, ArticleAnnouncement
from ..database.articles import select_articles_announcement, select_article, insert_articles, delete_articles, select_article_images

feed_router: APIRouter = APIRouter(
	prefix="/feed",
	tags=["Маршруты для получения статей пользователей"]
)
logger: Logger = configure_logs(__name__)


@feed_router.get("/articles")
@verify_jwt
async def get_articles(authorization: str = Header(...), login: Optional[str] = None):
	try:
		articles_data: list[ArticleAnnouncement] = select_articles_announcement(login)
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


@feed_router.get("/article_images")
@verify_jwt
async def get_article_images(article_id: int,  authorization: str = Header(...), max_amount: Optional[int] = None):
	try:
		article_images: list[tuple[bytes]] = select_article_images(article_id, max_amount)
		# Преобразуем список байтов в список Base64-строк
		encoded_images = [base64.b64encode(img).decode("utf-8") for (img,) in article_images]

		return JSONResponse(
			status_code=status.HTTP_200_OK,
			content={"images": encoded_images}
		)
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@feed_router.post("/add_article")
@verify_jwt
async def add_article(article_data: ArticleData, authorization: str = Header(...)):
	try:
		insert_articles([article_data])
		return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "success"})
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@feed_router.post("/remove_article")
@verify_jwt
async def remove_article(article_id: int, authorization: str = Header(...)):
	try:
		delete_articles(article_id)
		return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "success"})
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
