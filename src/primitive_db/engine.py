import prompt

from .consts import META_LOCATION
from .core import create_table, drop_table, list_tables
from .parser import parse_command, parse_pairs
from .utils import load_metadata, save_metadata


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
        
