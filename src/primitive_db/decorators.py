"""Декораторы и замыкание для кэширования."""
import time
from functools import wraps


def handle_db_errors(func):
    """Перехватывает ошибки функции и печатает сообщение вместо traceback."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден. "
                  "Возможно, база данных не инициализирована.")
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
    return wrapper


def confirm_action(action_name):
    """Спрашивает подтверждение перед выполнением опасной операции."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return args[0]   # возвращаем данные без изменений
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func):
    """Замеряет время выполнения функции и печатает его."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result
    return wrapper


def create_cacher():
    """Возвращает функцию, которая хранит кэш результатов в замыкании."""
    cache = {}

    def cache_result(key, value_func):
        """Возвращает результат из кэша или считает его и запоминает."""
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    cache_result.clear = cache.clear
    return cache_result