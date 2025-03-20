from logging import Logger
from collections.abc import Callable
from datetime import datetime, timezone, timedelta
from functools import wraps
from typing import Optional

import jwt
from jwt import InvalidTokenError, ExpiredSignatureError
from fastapi import HTTPException, Header, status

from .logger import configure_logs
from .static import SECRET_KEY, ALGORITHM

logger: Logger = configure_logs(__name__)

def verify_jwt_token(f: Callable) -> Optional[Callable]:
    @wraps(f)
    async def wrapper(authorization: str = Header(...), **kwargs) -> Optional[Callable]:
        """
        Функция-проверка JWT токена, передаваемого в заголовке Authorization.
        Ожидается формат: "Bearer <token>"
        """
        try:
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
        return await f(authorization, **kwargs)
    return wrapper


def create_jwt_token(login: str, lifetime=timedelta(days=1)) -> str:
    """
    Создаёт JWT токен
    :param login: Логин пользователя
    :param lifetime: Время жизни токена
    :return: JWT токен в формате строки
    """
    return jwt.encode({
        "username": login,
        "exp": datetime.now(tz=timezone.utc) + lifetime,
    }, SECRET_KEY, algorithm=ALGORITHM)
