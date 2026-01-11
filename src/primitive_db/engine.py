import prompt
from prettytable import PrettyTable

from src.decorators import handle_db_errors

from .consts import META_LOCATION
from .core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
from .parser import parse_clause, parse_command, parse_pairs
from .utils import load_metadata, load_table_data, save_metadata, save_table_data


def print_help():
    """Prints the help message for the current mode."""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...)"
          " - создать запись.")
    print("<command> select from <имя_таблицы> where <столбец> = <значение>"
          " - прочитать записи по условию.")
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1>"
          " where <столбец_условия> = <значение_условия> - обновить запись.")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение>"
          " - удалить запись.")
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")

    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def print_rows_pretty(table_name: str, rows: list[dict], metadata: dict) -> None:
    """Выводит записи таблицы в форматированном виде.

    Args:
        table_name (str): Имя таблицы.
        rows (list[dict]): Список записей для вывода.
        metadata (dict): Метаданные всех таблиц.
    """
    schema = metadata.get(table_name, {})
    columns = ["ID"] + [c for c in schema.keys() if c != "ID"]
    if columns == ["ID"] and "ID" not in rows[0]:
        columns = list(rows[0].keys() if rows else [])
    t = PrettyTable()
    t.field_names = columns
    for r in rows:
        t.add_row([r.get(c, "") for c in columns])
    print(t)

@handle_db_errors
def parse_clause_safe(clause_str: str) -> dict:
    """Безопасно парсит строку условия с обработкой ошибок.

    Args:
        clause_str (str): Строка с условием для парсинга.

    Returns:
        dict: Словарь с разобранным условием.
    """
    return parse_clause(clause_str)

def handle_command(cmd: str, args: list[str], metadata: dict):
    """Обрабатывает команду пользователя.

    Args:
        cmd (str): Название команды.
        args (list[str]): Аргументы команды.
        metadata (dict): Метаданные всех таблиц.

    Returns:
        tuple: Кортеж из трех элементов:
            - app_over (bool): Флаг завершения работы приложения.
            - metadata (dict): Обновленные метаданные.
            - is_successful (bool): Флаг успешного выполнения команды.
    """
    app_over = False
    is_successful = False
    match cmd:
        case "create_table":
            if len(args) < 2:
                print("Недостаточно аргументов для создания таблицы. "
                    "Требуется имя таблицы и хотя бы один столбец. Попробуйте снова.")
                return app_over, metadata, is_successful
            invalid = parse_pairs(args[1:])
            if invalid:
                print(f"Некорректное значение: {invalid}. Попробуйте снова.")
                return app_over, metadata, is_successful
            new_meta = create_table(
                metadata,
                args[0],
                dict(arg.split(":") for arg in args[1:]),
            )
            if new_meta is not None:
                metadata = new_meta
                is_successful = True
        case "list_tables":
            if args:
                print(f"Некорректное значение: {' '.join(args)}. Попробуйте снова.")
                return app_over, metadata, is_successful
            list_tables(metadata)
        case "drop_table":
            if len(args) != 1:
                print("Некорректное значение. Требуется указать одно имя таблицы. "
                    "Попробуйте снова."
                )
                return app_over, metadata, is_successful
            new_meta = drop_table(metadata, args[0])
            if new_meta is not None:
                metadata = new_meta
                is_successful = True
        case "insert":
            if len(args) < 4 or args[0].lower() != "into" or \
             args[2].lower() != "values":
                print("Некорректный синтаксис команды insert. Попробуйте снова.")
                return app_over, metadata, is_successful
            table_name = args[1]
            new_data = insert(metadata, table_name, args[3:])
            if new_data is not None:
                save_table_data(table_name, new_data)
        case "select":
            if len(args) < 2 or args[0].lower() != "from":
                print("Некорректный синтаксис команды select. Попробуйте снова.")
                return app_over, metadata, is_successful
            table_name = args[1]
            if table_name not in metadata:
                print(f'Таблица "{table_name}" не существует.')
                return app_over, metadata, is_successful
            table_data = load_table_data(table_name)
            if len(args) == 2:
                rows = select(table_data, {})
                if not rows:
                    print("Нет записей.")
                else:
                    print_rows_pretty(table_name, rows, metadata)
                return app_over, metadata, is_successful
            if len(args) < 4 or args[2].lower() != "where" or args.count("where") != 1:
                print("Некорректный синтаксис команды select. Попробуйте снова.")
                return app_over, metadata, is_successful
            clause = parse_clause_safe(" ".join(args[3:]))
            if clause is None:
                return app_over, metadata, is_successful
            rows = select(table_data, clause)
            if not rows:
                print("Нет записей.")
            else:
                print_rows_pretty(table_name, rows, metadata)
        case "update":
            if len(args) < 5:
                print("Недостаточно аргументов для обновления записи."
                      " Попробуйте снова.")
                return app_over, metadata, is_successful
            table_name = args[0]
            if table_name not in metadata:
                print(f'Таблица "{table_name}" не существует.')
                return app_over, metadata, is_successful
            if args[1].lower() != "set" or args.count("where") != 1:
                print("Некорректный синтаксис команды update. Попробуйте снова.")
                return app_over, metadata, is_successful
            seters, wheres = " ".join(args[2:]).split("where", 1)
            set_clause = parse_clause_safe(seters)
            where_clause = parse_clause_safe(wheres)
            if set_clause is None or where_clause is None:
                return app_over, metadata, is_successful
            table_data = load_table_data(table_name)
            new_data = update(table_data, set_clause, where_clause)
            if new_data is not None:
                save_table_data(table_name, new_data)
        case "delete":
            if (
                len(args) < 4
                or args[0].lower() != "from"
                or args[2].lower() != "where"
                or args.count("where") != 1
            ):
                print("Некорректный синтаксис команды delete. Попробуйте снова.")
                return app_over, metadata, is_successful
            table_name = args[1]
            if table_name not in metadata:
                print(f'Таблица "{table_name}" не существует.')
                return app_over, metadata, is_successful
            where_clause = parse_clause_safe(" ".join(args[3:]))
            table_data = load_table_data(table_name)
            new_data = delete(table_data, where_clause)
            if new_data is not None:
                save_table_data(table_name, new_data)
        case "info":
            if len(args) != 1:
                print(
                    "Некорректное значение. Требуется указать одно имя таблицы. "
                    "Попробуйте снова."
                )
                return app_over, metadata, is_successful
            table_name = args[0]
            info(metadata, table_name)
        case "exit":
            app_over = True
        case "help":
            print_help()
        case _:
            print(f"Функции {cmd} нет. Попробуйте снова.")
    return app_over, metadata, is_successful

def get_input(prompt_msg=">>>Введите команду: "):
    """Получает и парсит ввод пользователя.

    Args:
        prompt_msg (str): Сообщение для приглашения к вводу.

    Returns:
        tuple: Кортеж из команды и списка аргументов.
    """
    try:
        input_str = prompt.string(prompt_msg).strip() # type: ignore
        cmd, args = parse_command(input_str)
    except (KeyboardInterrupt, EOFError):
        cmd, args = "exit", []
    return cmd.lower(), args

def run():
    """Запускает основной цикл работы базы данных."""
    print("***База данных***\n")
    print_help()
    app_over = False
    if not load_metadata(META_LOCATION):
        save_metadata(META_LOCATION, {})
    while not app_over:
        metadata = load_metadata(META_LOCATION)
        cmd, args = get_input()
        app_over, metadata, sucess_ = handle_command(cmd, args, metadata)
        if sucess_:
            save_metadata(META_LOCATION, metadata)
        
