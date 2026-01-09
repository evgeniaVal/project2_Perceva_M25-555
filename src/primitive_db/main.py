from .engine import cycle, help


def main():
    print("Первая попытка запустить проект!\n\n***")
    help()
    while True:
        cycle()


if __name__ == "__main__":
    main()
