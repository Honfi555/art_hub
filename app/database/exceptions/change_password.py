__all__: list[str] = ["SamePasswordException", "OldPasswordMismatchException", "IncorrectLoginException"]

class IncorrectLoginException(Exception):
    """Исключение выбрасывается, когда указанный логин не найден в базе данных."""
    def __init__(self, message="Неверный логин. Пользователь не найден."):
        super().__init__(message)


class OldPasswordMismatchException(Exception):
    """Исключение выбрасывается, когда хэш старого пароля не совпадает с хранящимся в базе."""
    def __init__(self, message="Старый пароль неверный."):
        super().__init__(message)


class SamePasswordException(Exception):
    """Исключение выбрасывается, если новый пароль совпадает со старым."""
    def __init__(self, message="Новый пароль не может совпадать со старым."):
        super().__init__(message)
