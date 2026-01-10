from .utils import load_table_data, save_table_data


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

def insert(metadata, table_name, values):
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    if len(values) != len(metadata[table_name]) - 1:
        raise ValueError("Количество значений не соответствует количеству столбцов.")
    expected = [v for k, v in metadata[table_name].items() if k != "ID"]
    for exp_type, val in zip(expected, values):
        if exp_type == "str" and not isinstance(val, str):
            raise ValueError(f"Ожидалась строка, получено: {val}.")
        if exp_type == "int" and not val.isdigit():
            raise ValueError(f"Ожидалось целое число, получено: {val}.")
        elif exp_type == "bool" and not isinstance(val, bool):
            raise ValueError("Ожидалось булево значение (true/false),"
                             f" получено: {val}.")
    loaded_data = load_table_data(table_name)
    new_id = max(loaded_data.keys(), default=0) + 1
    loaded_data[new_id] = {col: val for col, val in zip(
        (k for k in metadata[table_name].keys() if k != "ID"), values)}
    save_table_data(table_name, loaded_data)
    print(f"Запись успешно добавлена с ID {new_id}.")

def select(table_data, where_clause=None):
    results = []
    for record_id, record in table_data.items():
        if where_clause is None or all(record.get(col) == val for col, val 
                                       in where_clause.items()):
            results.append((record_id, record))
    return results

def update(table_data, set_clause, where_clause=None):
    updated_count = 0
    for record_id, record in table_data.items():
        if where_clause is None or all(record.get(col) == val for col, val 
                                       in where_clause.items()):
            for col, val in set_clause.items():
                record[col] = val
            updated_count += 1
    return updated_count

def delete(table_data, where_clause):
    to_delete = [record_id for record_id, record in table_data.items()
                 if where_clause is None or all(record.get(col) == val 
                                               for col, val in where_clause.items())]
    for record_id in to_delete:
        del table_data[record_id]
    return len(to_delete)
