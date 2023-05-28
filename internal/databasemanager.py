from motor.motor_asyncio import AsyncIOMotorClient

instance = None


def init(dburl, dbname):
    global instance
    client = AsyncIOMotorClient(dburl)
    instance = client.get_database(dbname)
