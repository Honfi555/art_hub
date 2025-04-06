from logging import Logger

from fastapi import APIRouter, Header, status, HTTPException
from fastapi.responses import JSONResponse

from ..logger import configure_logs
from ..dependecies import verify_jwt
from ..models.user_info import AuthorInfo
from ..database.users import select_user_info

users_router: APIRouter = APIRouter(
	prefix="/users",
	tags=["Маршруты для получения информации о пользователях"]
)
logger: Logger = configure_logs(__name__)


@users_router.get("/author")
@verify_jwt
async def get_author(author_name: str, authorization: str = Header(...)):
	try:
		author_info: AuthorInfo = select_user_info(username=author_name)
		return JSONResponse(status_code=status.HTTP_200_OK, content={"author_info": author_info})
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
