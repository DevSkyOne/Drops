import logging
from pathlib import Path

import discord
from discord.ext import commands

from Bot.data.config import *

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s#%(name)s: %(message)s')
log = logging.getLogger('BOT-MAIN')

intents: discord.Intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('ds!'),
    strip_after_prefix=True,
    sync_commands=True,
    delete_not_existing_commands=True,
    activity=discord.Game('Hosting your Bot')
)


def load_bot():
    log.info('Starting...')
    log.info("Initialising Database...")
    cogs = [p.stem for p in Path('Bot/cogs').glob('**/*.py') if not p.name.startswith('__')]
    log.info('Loading %d extensions...', len(cogs))

    for cog in cogs:
        bot.load_extension(f'Bot.cogs.{cog}')
        log.info('Loaded %s', cog)

    bot.run(TOKEN)
