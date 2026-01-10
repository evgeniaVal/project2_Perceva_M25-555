from .utils import load_table_data


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

    schema = metadata[table_name]

    columns = [(col, typ) for col, typ in schema.items() if col != "ID"]

    if len(values) != len(columns):
        raise ValueError("Количество значений не соответствует количеству столбцов.")

    table_data = load_table_data(table_name)
    if table_data is None:
        table_data = []

    if table_data:
        new_id = max(int(row.get("ID", 0)) for row in table_data) + 1
    else:
        new_id = 1

    record = {"ID": new_id}

    for (col_name, col_type), raw in zip(columns, values):
        if col_type == "int":
            try:
                record[col_name] = int(raw)
            except ValueError:
                raise ValueError(f"Некорректное значение: {raw}. Ожидалось int.")
        elif col_type == "bool":
            low = raw.strip().lower()
            if low == "true":
                record[col_name] = True
            elif low == "false":
                record[col_name] = False
            else:
                raise ValueError(
                    f"Некорректное значение: {raw}. Ожидалось bool (true/false)."
                )
        elif col_type == "str":
            record[col_name] = raw
        else:
            raise ValueError(f"Недопустимый тип столбца: {col_type}.")

    table_data.append(record)
    return table_data

    

def select(table_data, where_clause=None):
    results = []
    for row in table_data:
        if where_clause is None or all(row.get(col) == val for col, val in 
                                       where_clause.items()):
            results.append(row)
    return results

def update(table_data, set_clause, where_clause):
    updated_count = 0
    for row in table_data:
        if where_clause is None or all(row.get(col) == val for col, val in 
                                       where_clause.items()):
            for col, val in set_clause.items():
                row[col] = val
            updated_count += 1
    return updated_count

def delete(table_data, where_clause):
    if where_clause is None:
        raise ValueError("Некорректное значение: условие where обязательно для delete.")

    new_data: list[dict] = []
    deleted_count = 0

    for row in table_data:
        if all(row.get(col) == val for col, val in where_clause.items()):
            deleted_count += 1
        else:
            new_data.append(row)

    return new_data, deleted_count
