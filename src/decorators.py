from functools import wraps


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
