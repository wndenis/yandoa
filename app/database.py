from . import config
import motor.motor_asyncio


class Cols:
    def __init__(self, files_collection, history_collection):
        self.files_collection = files_collection
        self.history_collection = history_collection


async def get_cols():
    try:
        return get_cols.cols
    except:
        pass
    auth_str = f"mongodb://{config.MONGO_USER}:{config.MONGO_PASS}@{config.MONGO_HOST}"
    # print(auth_str)
    client = motor.motor_asyncio.AsyncIOMotorClient(
        auth_str,
        serverSelectionTimeoutMS=5000)
    try:
        await client.server_info()
    except Exception as e:
        print("Unable to connect to the server.", e)
        exit(1)
    db = client.database

    # Create the database for our example (we will use the same database throughout the tutorial
    cols = Cols(db['docs'], db['history'])
    get_cols.cols = cols
    return cols
