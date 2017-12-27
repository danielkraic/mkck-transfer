from config import DEBUG


def debug(message: str) -> None:
    if DEBUG:
        print(message)
