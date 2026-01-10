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

def save_metadata(filepath: str, data: dict) -> None:
    """Сохраняет метаданные в json файл.

    Args:
        filepath (str): Путь к json файлу для сохранения метаданных.
        data (dict): Метаданные в виде словаря для сохранения.
    """
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except (FileNotFoundError, PermissionError, 
            IsADirectoryError, NotADirectoryError, UnicodeEncodeError) as e:
        print(f"Не удалось сохранить в {filepath}: {e}")
    except (TypeError, ValueError, OverflowError) as err:
        print(f"Не удалось записать данные в JSON для {filepath}: {err}")    
