import os


def getenv(name):
    val = os.getenv(name)
    if val is None:
        print(f"{name} is not specified but required in order to run")
        exit(1)
    return val

MONGO_USER = getenv("MONGO_USER")
MONGO_PASS = getenv("MONGO_PASS")
MONGO_HOST = getenv("MONGO_HOST")
