from .engine import cycle, print_help


def main():
    print("Первая попытка запустить проект!\n\n***")
    print_help()
    while True:
        cycle()


if __name__ == "__main__":
    main()
