import shlex

import prompt

from .consts import META_LOCATION
from .core import create_table, drop_table, list_tables
from .utils import check_tokens, load_metadata, save_metadata


def run():
    print("***База данных***\n")
    print_help()
    app_over = False
    if not load_metadata(META_LOCATION):
        save_metadata(META_LOCATION, {})
    while not app_over:
        metadata = load_metadata(META_LOCATION)
        try:
            input_str = prompt.string(">>>Введите команду: ").strip().lower() # type: ignore
            args = shlex.split(input_str)
            if not args:
                continue
        except (KeyboardInterrupt, EOFError):
            args = ["exit"]
        match args[0]:
            case "create_table":
                if len(args) < 3:
                    print("Недостаточно аргументов. Попробуйте снова.")
                    continue
                invalid = check_tokens(args[2:], 
                                       lambda x: x.count(":") == 1 and 
                                       all(i_part for i_part in x.split(":")))
                if invalid:
                    print(f"Некорректное значение: {invalid}. Попробуйте снова.")
                    continue
                try:
                    save_metadata(META_LOCATION, create_table(metadata, args[1], 
                                dict(arg.split(":") for arg in args[2:])))
                except (ValueError,) as e:
                    print(f"{e}")
            case "list_tables":
                list_tables(metadata)
            case "drop_table":
                if len(args) < 2:
                    print("Недостаточно аргументов. Попробуйте снова.")
                    continue
                elif len(args) > 2:
                    print(f"Некорректное значение: {' '.join(args[2:])}." 
                          "Попробуйте снова.")
                    continue
                try:
                    save_metadata(META_LOCATION, drop_table(metadata, *args[1:]))
                except (ValueError,) as e:
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
