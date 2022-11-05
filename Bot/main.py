import asyncio
import logging
from pathlib import Path
import i18n

import discord
from discord.ext import commands

from Bot.data.config import *
from Database import get_pool
import aiomysql
import aiofiles

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s#%(name)s: %(message)s')
log = logging.getLogger('BOT-MAIN')

intents: discord.Intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('dr!'),
    strip_after_prefix=True,
    sync_commands=True,
    delete_not_existing_commands=True,
    intents=intents,
    activity=discord.Activity(type=discord.ActivityType.competing, name='Searching for drops'),
)


async def init_db() -> None:
    pool: aiomysql.Pool = await get_pool()
    async with aiofiles.open("Database/structure.sql", "r") as fp:
        struct = await fp.read()

    async with pool.acquire() as connection:
        connection: aiomysql.Connection
        cursor: aiomysql.Cursor = await connection.cursor()
        for query in struct.split(";"):
            try:
                await cursor.execute(query)
            except Exception as e:
                log.error(e)
                continue
    pool.close()
    await pool.wait_closed()


def load_bot():
    log.info('Starting...')
    log.info('Loading translations...')
    i18n.set('file_format', 'json')
    i18n.set('filename_format', '{locale}.{format}')
    i18n.load_path.append(Path('Bot/data/locales'))
    i18n.set('fallback', 'en')
    i18n.set('locale', 'de')
    log.info('Translations loaded.')
    log.info("Initialising Database...")
    asyncio.run(init_db())
    cogs = [p.stem for p in Path('Bot/cogs').glob('**/*.py') if not p.name.startswith('__')]
    log.info('Loading %d extensions...', len(cogs))

    for cog in cogs:
        bot.load_extension(f'Bot.cogs.{cog}')
        log.info('Loaded %s', cog)

    bot.run(TOKEN)
