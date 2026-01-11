from functools import wraps
from time import monotonic


def handle_db_errors(func):
    """Декоратор для обработки ошибок при работе с базой данных.

    Перехватывает и обрабатывает различные типы исключений,
    возникающие при работе с базой данных, выводя информативные
    сообщения об ошибках вместо падения программы.

    Args:
        func: Декорируемая функция.

    Returns:
        Обёрнутая функция с обработкой ошибок.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден. Возможно, база данных"
                  " не инициализирована.")
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
    return wrapper


def confirm_action(action_name):
    """Декоратор для запроса подтверждения перед выполнением действия.

    Перед выполнением декорированной функции запрашивает подтверждение
    у пользователя. Если пользователь не подтверждает действие (не вводит 'y'),
    функция не выполняется.

    Args:
        action_name (str): Название действия для отображения в запросе подтверждения.

    Returns:
        function: Декоратор для функции.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            ).strip().lower()

            if answer != "y":
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator

def log_time(func):
    """Декоратор для логирования времени выполнения функции.

    Args:
        func: Декорируемая функция.

    Returns:
        Обёрнутая функция с логированием времени выполнения.
    """
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = monotonic()
        result = func(*args, **kwargs)
        end_time = monotonic()
        elapsed_time = end_time - start_time
        print(f"Функция {func.__name__} выполнилась за {elapsed_time:.3f} секунд")
        return result
    return wrapper

def create_cacher():
    cache= {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        value = value_func()
        cache[key] = value
        return value
    def clear():
        cache.clear()

    cache_result.clear = clear # type:ignore
    return cache_result
