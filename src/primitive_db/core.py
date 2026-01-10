def create_table(metadata: dict, table_name: str, columns: dict) -> dict:
    """Создает новую таблицу в метаданных.

    Args:
        metadata (dict): Метаданные всех таблиц.
        table_name (str): Имя создаваемой таблицы.
        columns (dict): Словарь с именами и типами столбцов.

    Raises:
        ValueError: Если столбец с именем 'ID' присутствует в columns.
        ValueError: Если таблица с таким именем уже существует.
        ValueError: Если тип столбца недопустим.

    Returns:
        dict: Обновленные метаданные с добавленной таблицей.
    """
    if 'ID' in columns:
        raise ValueError("Столбец с именем 'ID' зарезервирован и " \
        "добавляется автоматически.")
    if table_name in metadata:
        raise ValueError(f"Таблица {table_name} уже существует.")
    if not all(col_type in {'int', 'str', 'bool'} for col_type in columns.values()):
        raise ValueError("Недопустимый тип столбца. Допустимые типы: int, str, bool.")
    return {**metadata, table_name: {"ID": "int", **columns}}

def drop_table(metadata: dict, table_name: str) -> dict:
    """Удаляет таблицу из метаданных.

    Args:
        metadata (dict): Метаданные всех таблиц.
        table_name (str): Имя удаляемой таблицы.
    Raises:
        ValueError: Если таблица с таким именем не существует.

    Returns:
        dict: Обновленные метаданные без удаленной таблицы.
    """
    if table_name not in metadata:
        raise ValueError(f"Таблица {table_name} не существует.")
    return {k: v for k, v in metadata.items() if k != table_name}
    
