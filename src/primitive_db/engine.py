import prompt
from prettytable import PrettyTable

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
    schema = metadata.get(table_name, {})
    columns = ["ID"] + [c for c in schema.keys() if c != "ID"]
    if columns == ["ID"] and "ID" not in rows[0]:
        columns = list(rows[0].keys())
    t = PrettyTable()
    t.field_names = columns
    for r in rows:
        t.add_row([r.get(c, "") for c in columns])
    print(t)

def handle_command(cmd, args, metadata):
    app_over = False
    is_successful = False
    try:
        match cmd:
            case "create_table":
                if len(args) < 2:
                    raise ValueError("Недостаточно аргументов для создания таблицы."
                                     " Требуется имя таблицы и хотя бы один столбец."
                                     " Попробуйте снова.")
                invalid = parse_pairs(args[1:])
                if invalid:
                    raise ValueError(f"Некорректное значение: {invalid}." 
                                     " Попробуйте снова.")
                metadata = create_table(metadata, args[0], 
                    dict(arg.split(":") for arg in args[1:]))
                is_successful = True
            case "list_tables":
                if args:
                    raise ValueError(f"Некорректное значение: {' '.join(args)}." 
                                     " Попробуйте снова.")
                list_tables(metadata)
            case "drop_table":
                if len(args) != 1:
                    raise ValueError("Некорректное значение. Требуется указать одно"
                                     " имя таблицы. Попробуйте снова.")
                metadata = drop_table(metadata, args[0])
                is_successful = True
            case "insert":
                if len(args) < 4 or args[0].lower() != "into" or \
                   args[2].lower() != "values":
                    raise ValueError("Некорректный синтаксис команды insert."
                                     " Попробуйте снова.")
                save_table_data(args[1], insert(metadata, args[1], 
                                [x.replace("(", "").replace(")", "").replace(',', "") 
                                 for x in args[3:]]))
            case "select":
                if len(args) < 2 or args[0].lower() != "from":
                    raise ValueError("Некорректный синтаксис команды select."
                                     " Попробуйте снова.")
                table_name = args[1]
                if table_name not in metadata:
                    raise ValueError(f'Таблица "{table_name}" не существует.')
                table_data = load_table_data(table_name)
                if len(args) == 2:
                    print_rows_pretty(table_name, select(table_data, {}), metadata)
                elif len(args) < 4 or args[2].lower() != "where" or \
                 args.count("where") != 1:
                    raise ValueError("Некорректный синтаксис команды select."
                                     " Попробуйте снова.")
                else:
                    clause = parse_clause(" ".join(args[3:]))
                    print_rows_pretty(table_name, select(table_data, clause), metadata)
            case "update":
                if len(args) < 5:
                    raise ValueError("Недостаточно аргументов для обновления записи."
                                     " Попробуйте снова.")
                table_name = args[0]
                if table_name not in metadata:
                    raise ValueError(f'Таблица "{table_name}" не существует.')
                if args[1].lower() != "set" or args.count("where") != 1:
                    raise ValueError("Некорректный синтаксис команды update."
                                     " Попробуйте снова.")
                seters, wheres = " ".join(args[2:]).split("where")
                set_clause = parse_clause(seters)
                for k, v in set_clause.items():
                    if k not in metadata[table_name]:
                        raise ValueError(f'Столбца "{k}" не существует в таблице'
                                         f' "{table_name}".')
                    if metadata[table_name][k] == "int":
                        try:
                            set_clause[k] = int(v)
                        except ValueError:
                            raise ValueError(f'Некорректное значение для столбца'
                                             f' "{k}". Ожидалось целое число.')
                    elif metadata[table_name][k] == "bool":
                        if isinstance(v, bool):
                            continue
                        if v.lower() == "true": # type: ignore
                            set_clause[k] = True
                        elif v.lower() == "false": # type: ignore
                            set_clause[k] = False
                        else:
                            raise ValueError(f'Некорректное значение для столбца'
                                             f' "{k}". Ожидалось true или false.')
                    elif metadata[table_name][k] == "str":
                        if not isinstance(v, str):
                            raise ValueError(f'Некорректное значение для столбца'
                                             f' "{k}". Ожидалась строка.')
                where_clause = parse_clause(wheres)
                table_data = load_table_data(table_name)
                save_table_data(table_name, update(table_data, set_clause, 
                                                   where_clause))
            case "delete":
                if len(args) < 4 or args[0].lower() != "from" or \
                   args[2].lower() != "where" or args.count("where") != 1:
                    raise ValueError("Некорректный синтаксис команды delete."
                                     " Попробуйте снова.")
                table_name = args[1]
                if table_name not in metadata:
                    raise ValueError(f'Таблица "{table_name}" не существует.')
                where_clause = parse_clause(" ".join(args[3:]))
                table_data = load_table_data(table_name)
                save_table_data(table_name, delete(table_data, where_clause))
            case "info":
                if len(args) != 1:
                    raise ValueError("Некорректное значение. Требуется указать одно"
                                     " имя таблицы. Попробуйте снова.")
                table_name = args[0]
                if table_name not in metadata:
                    raise ValueError(f'Таблица "{table_name}" не существует.')
                info(metadata, table_name)
            case "exit":
                app_over = True
            case "help":
                print_help()
            case _:
                print(f"Функции {cmd} нет. Попробуйте снова.")
    except (ValueError,) as e:
        print(e)
    return app_over, metadata, is_successful

def get_input(prompt_msg=">>>Введите команду: "):
    try:
        input_str = prompt.string(prompt_msg).strip() # type: ignore
        cmd, args = parse_command(input_str)
    except (KeyboardInterrupt, EOFError):
        cmd, args = "exit", []
    return cmd.lower(), args

def run():
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
        
