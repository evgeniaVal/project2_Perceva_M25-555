import prompt


def cycle():
    user_input = prompt.string("Введите команду: ")
    print()
    match user_input:
        case "exit":
            exit()
        case "help":
            help()
        case _:
            print("Неизвестная команда")

def help():
    print("<comand> exit - выйти из программы")
    print("<comand> help - справочная информация")
