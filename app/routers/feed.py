from logging import Logger

from fastapi import APIRouter, Header, status
from fastapi.responses import JSONResponse

from ..logger import configure_logs
from ..models.articles import ArticleData
from ..dependecies import verify_jwt_token


feed_router: APIRouter = APIRouter(
	prefix="/feed",
	tags=["Маршруты для получения статей пользователей"]
)
logger: Logger = configure_logs(__name__)


@feed_router.get("/articles")
@verify_jwt_token
async def get_articles(authorization: str = Header(...)):
	return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "All is Fine"})


@feed_router.get("/article")
@verify_jwt_token
async def get_article(user_id: int, article_id: int, authorization: str = Header(...)):
	pass


@feed_router.post("/add_article")
@verify_jwt_token
async def add_article(user_id: int, article_data: ArticleData, authorization: str = Header(...)):
	pass


@feed_router.post("/remove_article")
@verify_jwt_token
async def remove_article(user_id: int, article_id: int, authorization: str = Header(...)):
	pass
