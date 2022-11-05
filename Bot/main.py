import logging
from pathlib import Path
import i18n

import discord
from discord.ext import commands

from Bot.data.config import *

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


def load_bot():
    log.info('Starting...')
    log.info('Loading translations...')
    i18n.set('file_format', 'json')
    i18n.set('filename_format', '{locale}.{format}')
    i18n.load_path.append(Path('Bot/data/locales'))
    i18n.set('fallback', 'en')
    i18n.set('locale', 'de')
    log.info('Translations loaded.')
    cogs = [p.stem for p in Path('Bot/cogs').glob('**/*.py') if not p.name.startswith('__')]
    log.info('Loading %d extensions...', len(cogs))

    for cog in cogs:
        bot.load_extension(f'Bot.cogs.{cog}')
        log.info('Loaded %s', cog)

    bot.run(TOKEN)
