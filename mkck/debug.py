from mkck.config import DEBUG, NOTICE


def debug(message: str) -> None:
    if DEBUG:
        print(message)


def notice(message: str) -> None:
    if NOTICE:
        print(message)
