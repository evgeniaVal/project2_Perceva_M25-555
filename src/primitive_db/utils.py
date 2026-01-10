import json


def load_metadata(filepath: str) -> dict:
    """Загружает метаданные из json файла.

    Args:
        filepath (str): Путь к json файлу с метаданными.

    Returns:
        dict: Метаданные в виде словаря. В случае ошибки возвращается пустой словарь.
    """
    try:
        with open(filepath) as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, PermissionError, 
            IsADirectoryError, NotADirectoryError, UnicodeDecodeError) as e:
        print(f"Не удалось открыть {filepath}: {e}")
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON из файла {filepath}: {e}")
    return {}
