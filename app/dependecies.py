from logging import Logger
from collections.abc import Callable
from datetime import datetime, timezone, timedelta
from functools import wraps
from typing import Optional

import jwt
from jwt import InvalidTokenError, ExpiredSignatureError
from fastapi import HTTPException, status

from .logger import configure_logs
from .static import SECRET_KEY, ALGORITHM

logger: Logger = configure_logs(__name__)


def check_jwt_token(token: str) -> Optional[dict]:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Отсутствует заголовок авторизации",
        )
    scheme, _, token = token.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный формат заголовка авторизации",
        )

    return jwt.decode(jwt=token, key=SECRET_KEY, algorithms=ALGORITHM)


def verify_jwt(f: Callable) -> Optional[Callable]:
    @wraps(f)
    async def wrapper(*args, **kwargs) -> Optional[Callable]:
        """
        Функция-проверка JWT, передаваемого в заголовке Authorization.
        Ожидается формат: "Bearer <token>"
        """
        try:
            authorization = kwargs.get("authorization")
            check_jwt_token(authorization)
        except ExpiredSignatureError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Срок действия токена истек")
        except InvalidTokenError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Недействительный токен")
        return await f(*args, **kwargs)
    return wrapper


def create_jwt(login: str, lifetime=timedelta(days=1)) -> str:
    """
    Создаёт JWT.
    :param login: Логин пользователя
    :param lifetime: Время жизни токена
    :return: JWT в формате строки
    """
    return jwt.encode({
        "username": login,
        "exp": datetime.now(tz=timezone.utc) + lifetime,
    }, SECRET_KEY, algorithm=ALGORITHM)


def get_jwt_login(authorization: str) -> str:
    decoded_info: dict | None = check_jwt_token(authorization)

    if decoded_info is None or len(decoded_info) == 0:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный payload токена")

    return decoded_info["username"]