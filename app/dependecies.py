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


def verify_jwt(f: Callable) -> Optional[Callable]:
    @wraps(f)
    async def wrapper(*args, **kwargs) -> Optional[Callable]:
        """
        Функция-проверка JWT, передаваемого в заголовке Authorization.
        Ожидается формат: "Bearer <token>"
        """
        try:
            authorization = kwargs.get("authorization")
            if not authorization:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Отсутствует заголовок авторизации",
                )
            scheme, _, token = authorization.partition(" ")
            if scheme.lower() != "bearer" or not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверный формат заголовка авторизации",
                )

            jwt.decode(jwt=token, key=SECRET_KEY, algorithms=ALGORITHM)
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
