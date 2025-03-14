import logging
import hashlib

from psycopg2 import extensions
from psycopg2.extras import DictCursor
from psycopg2 import OperationalError, InterfaceError, errors

from .connect import connect
from .exceptions.change_password import *

UserData = dict[str, any]


def insert_user(cur: extensions.cursor, user: dict) -> bool:
    """
    Вставляет запись в таблице users.users.
    Возвращает True, если операция прошла успешно, иначе False.
    """
    try:
        query = """
            INSERT INTO users.users (
                login, password, description
            ) VALUES (%s, %s, %s);
        """
        params = (
            user.get('login'),
            hashlib.sha256(user.get('password').encode('utf-8'), usedforsecurity=True).hexdigest(),
            user.get('description')
        )
        logging.debug("Вставка пользователя с login %s", user.get('login'))
        cur.execute(query, params)
        logging.debug("Пользователь с login %s успешно вставлен.", user.get('login'))
        return True
    except errors.UniqueViolation as e:
        logging.exception("Пользователь с login %s уже существует: %s", user.get('login'), e)
        raise
    except Exception as e:
        logging.exception("Ошибка при вставке пользователя с login %s: %s", user.get('login'), e)
        return False


def change_password(login: str, old_password: str, new_password: str) -> bool:
    conn = None
    try:
        conn = connect()
        with conn.cursor() as cur:
            query_select: str = "SELECT password FROM users.users WHERE login = %s;"
            cur.execute(query_select, (login, ))
            password: str | None = cur.fetchone()

            if password is None:
                raise IncorrectLoginException(f"Логин {login} не найден")

            if password[0] != hashlib.sha256(old_password.encode('utf-8'), usedforsecurity=True).hexdigest():
                logging.info("1")
                raise OldPasswordMismatchException("Неверный старый пароль")

            if old_password == new_password:
                raise SamePasswordException("Новый пароль совпадает со старым")

            query_update = "UPDATE users.users SET password = %s WHERE login = %s;"
            cur.execute(query_update,
                        (hashlib.sha256(new_password.encode('utf-8'), usedforsecurity=True).hexdigest(), login))
            conn.commit()
            logging.debug("Пароль успешно изменён для пользователя с login %s", login)
            return True
    except (OperationalError, InterfaceError) as e:
        logging.error("Ошибка соединения: %s", e)
        return False
    finally:
        if conn:
            conn.close()


def process_user(user: dict) -> bool:
    """
    Обрабатывает и вставляет пользователя в базу данных.
    Использует метод static.connect() для получения соединения.
    """
    logging.info("Начало обработки пользователя %s.", user.get('login'))
    conn = None
    try:
        conn = connect()  # Получаем соединение через static.connect()
        conn.autocommit = False  # Явное управление транзакциями
        with conn.cursor(cursor_factory=DictCursor) as cur:
            # Устанавливаем search_path для использования схемы users
            cur.execute("SET search_path TO users, public;")
            logging.debug("Поисковый путь установлен на схемы 'users' и 'public'.")

        with conn.cursor(cursor_factory=DictCursor) as cur:
            if not insert_user(cur, user):
                conn.rollback()
                logging.error("Ошибка вставки пользователя %s, транзакция откатилась.", user.get('login'))
                return False

        conn.commit()
        logging.info("Транзакция зафиксирована для пользователя %s.", user.get('login'))
        return True
    except (OperationalError, InterfaceError) as e:
        if conn:
            conn.rollback()
        logging.error("Ошибка соединения для пользователя %s. Ошибка: %s", user.get('login'), e)
    except errors.UniqueViolation as e:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error("Транзакция откатилась для пользователя %s. Ошибка: %s", user.get('login'), e)
    finally:
        if conn:
            conn.close()


def check_credentials(login: str, password: str) -> bool:
    """
    Проверяет корректность логина и пароля, подключаясь напрямую к базе данных.
    """
    logging.info("Начало проверки учетных данных в базе данных.")
    conn = None
    try:
        # Прямое подключение к базе данных без пула соединений
        conn = connect()
        with conn.cursor() as cur:
            query = """
                SELECT CASE 
                    WHEN EXISTS (
                        SELECT 1 
                        FROM users.users 
                        WHERE login = %s AND password = %s
                    ) 
                    THEN true 
                    ELSE false 
                END AS is_valid;
            """
            hashed_password = hashlib.sha256(password.encode('utf-8'), usedforsecurity=True).hexdigest()
            cur.execute(query, (login, hashed_password))
            result = bool(cur.fetchone()[0])
            logging.info("Результат проверки учетных данных: %s", result)
            return result
    except (OperationalError, InterfaceError) as e:
        logging.error("Ошибка соединения: %s", e)
        raise
    except Exception as e:
        logging.error("Ошибка при выполнении запроса: %s", e)
        raise
    finally:
        if conn:
            conn.close()


def check_login(login: str) -> bool:
    """
    Проверяет корректность логина, подключаясь напрямую к базе данных.
    """
    logging.info("Начало проверки логина в базе данных.")
    conn = None
    try:
        # Прямое подключение к базе данных без пула соединений
        conn = connect()
        with conn.cursor() as cur:
            query = """
                SELECT CASE 
                    WHEN EXISTS (
                        SELECT 1 
                        FROM users.users 
                        WHERE login = %s
                    ) 
                    THEN true 
                    ELSE false 
                END AS is_valid;
            """
            cur.execute(query, (login, ))
            result = bool(cur.fetchone()[0])
            logging.info("Результат проверки логина: %s", result)
            return result
    except (OperationalError, InterfaceError) as e:
        logging.error("Ошибка соединения: %s", e)
        raise
    except Exception as e:
        logging.error("Ошибка при выполнении запроса: %s", e)
        raise
    finally:
        if conn:
            conn.close()
