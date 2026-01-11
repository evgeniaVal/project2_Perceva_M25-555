import json
import os

from .consts import DATA_FOLDER


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
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_metadata(filepath: str, data: dict) -> None:
    """Сохраняет метаданные в json файл.

    Args:
        filepath (str): Путь к json файлу для сохранения метаданных.
        data (dict): Метаданные в виде словаря для сохранения.
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def load_table_data(table_name):
    """Загружает данные таблицы из json.

    Args:
        table_name (str): Имя таблицы для загрузки данных.

    Returns:
        list: Данные в виде списка. В случае ошибки возвращается пустой список.
    """
    try:
        with open(f'{DATA_FOLDER}/{table_name}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_table_data(table_name, data):
    """Сохраняет данные таблицы в json файл.

    Args:
        table_name (str): Имя таблицы для сохранения данных.
        data (list): Данные в виде списка для сохранения.
    """
    os.makedirs(DATA_FOLDER, exist_ok=True)
    with open(f'{DATA_FOLDER}/{table_name}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
