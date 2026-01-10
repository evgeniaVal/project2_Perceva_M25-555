import shlex

import prompt

from .core import create_table, drop_table, list_tables
from .utils import load_metadata, save_metadata


def run():
    print("***База данных***\n")
    print_help()
    app_over = False
    if not load_metadata("db_meta.json"):
        save_metadata("db_meta.json", {})
    while not app_over:
        metadata = load_metadata("db_meta.json")
        try:
            input_str = prompt.string(">>>Введите команду: ").strip() # type: ignore
            args = shlex.split(input_str)
            if not args:
                continue
        except (KeyboardInterrupt, EOFError):
            args = ["exit"]
        match args[0].lower():
            case "create_table":
                if len(args) < 3:
                    print("Недостаточно аргументов. Попробуйте снова.")
                    continue
                try:
                    save_metadata("db_meta.json", create_table(metadata, args[1], 
                                dict(arg.split(":") for arg in args[2:])))
                except (ValueError,TypeError) as e:
                    print(f"{e}")
            case "list_tables":
                list_tables(metadata)
            case "drop_table":
                if len(args) < 2:
                    print("Недостаточно аргументов. Попробуйте снова.")
                    continue
                try:
                    save_metadata("db_meta.json", drop_table(metadata, *args[1:]))
                except (ValueError, TypeError) as e:
                    print(f"{e}")
            case "exit":
                app_over = True
            case "help":
                print_help()
            case _:
                print(f"Функции {args[0]} нет. Попробуйте снова.")

# src/primitive_db/engine.py
def print_help():
    """Prints the help message for the current mode."""
   
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")
