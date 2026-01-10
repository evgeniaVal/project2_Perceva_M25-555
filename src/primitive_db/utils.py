import json


def load_metadata(filepath: str) -> dict:
    """Загружает метаданные из json файла.

    Args:
        filepath (str): Путь к json файлу с метаданными.

    Returns:
        dict: Метаданные в виде словаря. В случае ошибки возвращается пустой словарь.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return {}

def save_metadata(filepath: str, data: dict) -> None:
    """Сохраняет метаданные в json файл.

    Args:
        filepath (str): Путь к json файлу для сохранения метаданных.
        data (dict): Метаданные в виде словаря для сохранения.
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def check_tokens(tokens: list, func):
    for token in tokens:
        if not func(token):
            return token
    return ""
