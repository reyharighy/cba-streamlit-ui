# internal
from application import UserInterface


def main() -> None:
    """
    Docstring for main
    """
    app: UserInterface = UserInterface()
    app.run()


if __name__ == "__main__":
    main()