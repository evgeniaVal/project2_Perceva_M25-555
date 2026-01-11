from src.decorators import confirm_action, handle_db_errors, log_time

from .utils import load_table_data


@handle_db_errors
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

@handle_db_errors
@confirm_action("удаление таблицы")
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
        raise KeyError(table_name)
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

@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Вставляет новую запись в таблицу.

    Args:
        metadata (dict): Метаданные всех таблиц.
        table_name (str): Имя таблицы для вставки данных.
        values (list): Список значений для вставки.

    Raises:
        KeyError: Если таблица не существует.
        ValueError: Если количество значений не соответствует количеству столбцов.
        ValueError: Если тип значения не соответствует типу столбца.

    Returns:
        list: Обновленные данные таблицы с добавленной записью.
    """
    if table_name not in metadata:
        raise KeyError(table_name)
    
    cleaned = []
    for x in values:
        x = x.replace("(", "").replace(")", "").replace(",", "").strip()
        cleaned.append(x)
    values = cleaned

    schema = metadata[table_name]

    columns = [(col, typ) for col, typ in schema.items() if col != "ID"]

    if len(values) != len(columns):
        raise ValueError("Количество значений не соответствует количеству столбцов.")

    table_data = load_table_data(table_name)
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
            record[col_name] = raw.replace('""', '').replace("''", "")
        else:
            raise ValueError(f"Недопустимый тип столбца: {col_type}.")

    table_data.append(record)
    print(f'Запись с ID={record["ID"]} успешно добавлена в таблицу "{table_name}".')
    return table_data

    

def select(table_data, where_clause=None):
    """Выбирает записи из таблицы по условию.

    Args:
        table_data (list): Данные таблицы.
        where_clause (dict, optional): Условия фильтрации (столбец: значение).

    Returns:
        list: Список записей, соответствующих условию.
    """
    results = []
    for row in table_data:
        if not where_clause or all(row.get(col) == val for col, val in 
                                       where_clause.items()):
            results.append(row)
    return results

@log_time
def select_query(table_name, where_clause):
    table_data = load_table_data(table_name)
    where_clause = where_clause or {}
    return [row for row in table_data if all(row.get(k) == v for k, v in 
                                             where_clause.items())]

@handle_db_errors
@log_time
def update(table_data, set_clause, where_clause):
    """Обновляет записи в таблице по условию.

    Args:
        table_data (list): Данные таблицы.
        set_clause (dict): Словарь с обновляемыми столбцами и значениями.
        where_clause (dict): Условия для выбора записей для обновления.

    Raises:
        ValueError: Если не указано условие set.

    Returns:
        list: Обновленные данные таблицы.
    """
    updated_ids = []
    if not set_clause:
        raise ValueError("Условие set обязательно для update.")
    for row in table_data:
        if not where_clause or all(row.get(col) == val for col, val in 
                                       where_clause.items()):
            for col, val in set_clause.items():
                row[col] = val
            updated_ids.append(row.get("ID"))
    print(f"{len(updated_ids)} записей с ID: {', '.join(map(str, updated_ids))} успешно"
           " обновлено.")
    return table_data

@handle_db_errors
@confirm_action("удаление записей")
@log_time
def delete(table_data, where_clause):
    """Удаляет записи из таблицы по условию.

    Args:
        table_data (list): Данные таблицы.
        where_clause (dict): Условия для выбора записей для удаления.

    Raises:
        ValueError: Если не указано условие where.

    Returns:
        list: Данные таблицы без удаленных записей.
    """
    if not where_clause:
        raise ValueError("Условие where обязательно для delete.")

    new_data: list[dict] = []
    deleted_ids = []

    for row in table_data:
        if all(row.get(col) == val for col, val in where_clause.items()):
            deleted_ids.append(row.get("ID"))
        else:
            new_data.append(row)
    print(f"{len(deleted_ids)} записей с ID: {', '.join(map(str, deleted_ids))}"
          " успешно удалено.")
    return new_data

@handle_db_errors
@log_time
def info(metadata, table_name):
    """Выводит информацию о таблице.

    Args:
        metadata (dict): Метаданные всех таблиц.
        table_name (str): Имя таблицы для получения информации.

    Raises:
        KeyError: Если таблица не существует.
    """
    if table_name not in metadata:
        raise KeyError(table_name)
    print(f'Таблица: {table_name}')
    print(f"Столбцы: {', '.join(f'{col}:{typ}' for col, typ in 
                                metadata[table_name].items())}")
    print(f"Количество записей: {len(load_table_data(table_name))}")
