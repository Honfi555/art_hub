import logging

from fastapi import APIRouter, HTTPException, Header, status
from fastapi.responses import JSONResponse
from psycopg2.errors import UniqueViolation
from pydantic import BaseModel

from ..database.users import process_user, check_credentials, check_login, change_password
from ..database.exceptions.change_password import *
from ..dependecies import create_jwt_token, verify_jwt_token

router = APIRouter(
	prefix="/auth",
	tags=["Маршруты для действий с аккаунтом пользователя."]
)


class SignInData(BaseModel):
	login: str
	password: str


class ChangePasswordData(BaseModel):
	login: str
	old_password: str
	new_password: str


@router.post("/sign_in")
async def sign_in_route(data: SignInData):
	if not check_login(data.login):
		raise HTTPException(status.HTTP_404_NOT_FOUND, "Пользователь с таким логином не найден")
	if not check_credentials(data.login, data.password):
		raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Введён неверный пароль")
	return JSONResponse(content={"message": "Аутентификация пользователя прошла успешно",
								 "token": create_jwt_token(data.login)},
						status_code=status.HTTP_200_OK)


@router.post("/sign_up")
async def sign_up_route(data: SignInData):
	try:
		process_user(user={"login": data.login, "password": data.password, "description": ""})
		return JSONResponse(content={"message": "Пользователь успешно зарегистрирован",
									 "token": create_jwt_token(data.login)},
							status_code=status.HTTP_201_CREATED)
	except UniqueViolation:
		raise HTTPException(status.HTTP_409_CONFLICT, "Пользователь с таким логином уже существует")
	except Exception as e:
		logging.exception("Возникла непредвиденная ошибка при регистрации пользователя с логином %s. Ошибка: %s",
						  data.login, e)
		raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
							"Возникла непредвиденная ошибка на стороне сервера")


@router.post("/change_password")
async def change_password_route(data: ChangePasswordData, authorization: str = Header(...)):
	verify_jwt_token(authorization)

	try:
		if change_password(data.login, data.old_password, data.new_password):
			return JSONResponse(content={"message": "Пароль успешно сменён"}, status_code=status.HTTP_200_OK)
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
							detail="Непредвиденная ошибка, на стороне сервера")
	except (IncorrectLoginException, OldPasswordMismatchException) as e:
		logging.info("2")
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
	except SamePasswordException as e:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
