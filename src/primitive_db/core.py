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
    if 'id' in {x.lower() for x in columns}:
        raise ValueError("Столбец с именем 'ID' зарезервирован и " \
        "добавляется автоматически.")
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')
    if not all(col_type in {'int', 'str', 'bool'} for col_type in columns.values()):
        raise ValueError("Недопустимый тип столбца. Допустимые типы: int, str, bool.")
    metadata_tmp = {**metadata, table_name: {"ID": "int", **columns}}
    cols_str = ", ".join(f"{name}:{typ}" for name, typ in 
                         metadata_tmp[table_name].items())
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}.')
    return metadata_tmp

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
        raise ValueError(f'Таблица "{table_name}" не существует.')
    print(f'Таблица "{table_name}" успешно удалена.')
    return {k: v for k, v in metadata.items() if k != table_name}
    
def list_tables(metadata: dict) -> None:
    """Выводит список всех таблиц в метаданных.

    Args:
        metadata (dict): Метаданные всех таблиц.
    """
    if metadata:
        for table_name in metadata.keys():
            print(f"- {table_name}")
    else:
        print("Таблиц нет.")
