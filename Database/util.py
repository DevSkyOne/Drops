import aiomysql
from aiomysql import Pool

from Bot.data.config import DB_HOST, DB_NAME, DB_PASS, DB_USER


async def get_pool(autocommit: bool = True) -> Pool:
    HOST, PORT = DB_HOST.split(":")
    return await aiomysql.create_pool(
        host=HOST,
        port=int(PORT),
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME,
        autocommit=autocommit
    )
