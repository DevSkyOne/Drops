from . import *
from io import StringIO
from pathlib import Path


log = log_init(__file__)


class DevCommands(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot

    @commands.Cog.slash_command(
        base_name='extension',
        name='reload',
        description='reloads an extension',
        description_localizations=Localizations(german='Läd eine Extension neu'),
        default_required_permissions=discord.Permissions(administrator=True),
        options=[
            SlashCommandOption(
                name='name',
                description='The extension to reload',
                description_localizations=Localizations(german='Die Extension, die neu geladen werden soll'),
                option_type=str,
                min_length=3,
                max_length=100,
                autocomplete=True
            ),
            SlashCommandOption(
                name='sync-commands',
                description='Whether app-commands should be synced; default False',
                description_localizations=Localizations(
                    german='Ob App-Commands synchronisiert werden sollen; standardgemäß False'
                ),
                option_type=bool,
                required=False
            )
        ],
        connector={'sync-commands': 'sync_commands'}
    )
    @commands.is_owner()
    async def reload_extension(
            self,
            ctx: ApplicationCommandInteraction,
            name: str,
            sync_commands: bool = False
    ) -> None:
        if name == '__no_loaded_extension_with_this_name__':
            return await ctx.respond('There is no loaded extension with this name!', hidden=True, delete_after=5)  # type: ignore
        await ctx.defer(hidden=True)
        before = getattr(self.bot, 'sync_commands_on_cog_reload', False)
        self.bot.sync_commands_on_cog_reload = sync_commands
        try:
            self.bot.reload_extension(f'cogs.{name}')
            log.info(f'Reloaded extension \033[32m{name}\033[0m')
            await ctx.respond(
                f'The extension `{name}` has been successful reloaded{" and the app-commands synced." if sync_commands is True else "."}',
                hidden=True,
                delete_after=5
            )
        except commands.ExtensionNotLoaded:
            await ctx.respond(f'There is no extension with the name `{name}` loaded.', hidden=True, delete_after=5)
        except Exception as exc:
            file = StringIO('\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
            await ctx.respond(
                f'Es ist folgender Fehler beim Versuch die Extension `{name}` neu zuladen aufgetreten:',
                file=discord.File(file, filename='error.py'),
                hidden=True
            )
        self.bot.sync_commands_on_cog_reload = before

    @reload_extension.autocomplete_callback
    async def reload_extension_autocomplete(
            self,
            i: AutocompleteInteraction,
            name: str = None,
            sync_commands: bool = False
    ) -> None:
        name = name.lower() if name else ''
        # noinspection PyUnresolvedReferences
        loaded = [(n, c.__init__.__globals__['__file__'].split('\\')[-1].split('/')[-1].replace('.py', '')) for n, c in self.bot.cogs.items()]
        loaded_matching_name = [(f'{n} - cogs.{c}', c) for n, c in loaded if (n.lower().startswith(name) or c.startswith(name))]
        if loaded_matching_name:
            await i.send_choices([SlashCommandOptionChoice(n, c) for n, c in loaded_matching_name])
        else:
            await i.send_choices(
                [
                    SlashCommandOptionChoice('There is no loaded extension with this name.', '__no_loaded_extension_with_this_name__')
                ]
            )

    @commands.Cog.slash_command(
        base_name='extension',
        name='load',
        description='loads an extension',
        description_localizations=Localizations(german='Läd eine Extension'),
        default_required_permissions=discord.Permissions(administrator=True),
        options=[
            SlashCommandOption(
                name='name',
                description='The extension to load',
                description_localizations=Localizations(german='Die Extension, die geladen werden soll'),
                option_type=str,
                min_length=3,
                max_length=100,
                autocomplete=True
            ),
            SlashCommandOption(
                name='sync-commands',
                description='Whether app-commands should be synced; default False',
                description_localizations=Localizations(
                    german='Ob App-Commands synchronisiert werden sollen; standardgemäß False'
                ),
                option_type=bool,
                required=False
            )
        ],
        connector={'sync-commands': 'sync_commands'}
    )
    @commands.is_owner()
    async def load_extension(
            self,
            ctx: ApplicationCommandInteraction,
            name: str,
            sync_commands: bool = False
    ) -> None:
        if name == '__no_extension_to_load__':
            return await ctx.respond('There are no extensions to load!', hidden=True, delete_after=5)  # type: ignore
        await ctx.defer(hidden=True)
        before = getattr(self.bot, 'sync_commands_on_cog_reload', False)
        try:
            self.bot.load_extension(f'cogs.{name}')
            log.info(f'Loaded extension \033[32m{name}\033[0m')
            # noinspection PyProtectedMember
            await self.bot._request_sync_commands(is_cog_reload=True)
            await ctx.respond(
                f'The extension `{name}` has been successful loaded{" and the app-commands synced." if sync_commands is True else "."}',
                hidden=True,
                delete_after=5
            )
        except commands.ExtensionNotFound:
            await ctx.respond(f'Could not find an extension with the name `{name}`.', hidden=True, delete_after=5)
        except Exception as exc:
            file = StringIO('\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
            await ctx.respond(
                f'Es ist folgender Fehler beim Versuch die Extension `{name}` zu laden aufgetreten:',
                file=discord.File(file, filename='error.py'),
                hidden=True
            )
        self.bot.sync_commands_on_cog_reload = before

    @load_extension.autocomplete_callback
    async def load_extension_autocomplete(
            self,
            ctx: AutocompleteInteraction,
            name: str = None,
            sync_commands: bool = False
    ) -> None:
        extensions = [f'cogs.{p.stem}' for p in Path('./cogs/').glob('**/*.py') if not p.name.startswith('__')]
        loaded = list(self.bot.extensions)
        not_loaded = [SlashCommandOptionChoice(n) for n in extensions if n.startswith(name or '') and n not in loaded]
        if not_loaded:
            await ctx.send_choices(
                not_loaded
            )
        else:
            await ctx.send_choices(
                [
                    SlashCommandOptionChoice('There is no extension to load', '__no_extension_to_load__')
                ]
            )

    @commands.Cog.slash_command(
        base_name='extension',
        name='unload',
        description='unloads an extension',
        description_localizations=Localizations(german='Entlädt eine Extension'),
        default_required_permissions=discord.Permissions(administrator=True),
        options=[
            SlashCommandOption(
                name='name',
                description='The extension to unload',
                description_localizations=Localizations(german='Die Extension, die entladen werden soll'),
                option_type=str,
                min_length=3,
                max_length=100,
                autocomplete=True
            ),
            SlashCommandOption(
                name='sync-commands',
                description='Whether app-commands should be synced; default False',
                description_localizations=Localizations(
                    german='Ob App-Commands synchronisiert werden sollen; standardgemäß False'
                ),
                option_type=bool,
                required=False
            )
        ],
        connector={'sync-commands': 'sync_commands'}
    )
    @commands.is_owner()
    async def unload_extension(
            self,
            ctx: ApplicationCommandInteraction,
            name: str,
            sync_commands: bool = False
    ) -> None:
        if name == '__no_loaded_extension_with_this_name__':
            return await ctx.respond('There is no loaded extension with this name!', hidden=True, delete_after=5)  # type: ignore
        await ctx.defer(hidden=True)
        before = getattr(self.bot, 'sync_commands_on_cog_reload', False)
        self.bot.sync_commands_on_cog_reload = sync_commands
        try:
            self.bot.unload_extension(f'cogs.{name}')
            log.info(f'Unloaded extension \033[32m{name}\033[0m')
            # noinspection PyProtectedMember
            await self.bot._request_sync_commands(is_cog_reload=True)
            await ctx.respond(
                f'The extension `{name}` has been successful unloaded{" and the app-commands synced." if sync_commands is True else "."}',
                hidden=True,
                delete_after=5
            )
        except commands.ExtensionNotLoaded:
            await ctx.respond(f'There is no extension with the name `{name}` loaded.', hidden=True, delete_after=5)
        except Exception as exc:
            file = StringIO('\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
            await ctx.respond(
                f'Es ist folgender Fehler beim Versuch die Extension `{name}` zu entladen aufgetreten:',
                file=discord.File(file, filename='error.py'),
                hidden=True
            )
        self.bot.sync_commands_on_cog_reload = before

    @unload_extension.autocomplete_callback
    async def unload_extension_autocomplete(
            self,
            i: AutocompleteInteraction,
            name: str = None,
            sync_commands: bool = False
    ) -> None:
        name = name.lower() if name else ''
        # noinspection PyUnresolvedReferences
        loaded = [(n, c.__init__.__globals__['__file__'].split('\\')[-1].split('/')[-1].replace('.py', '')) for n, c in
                  self.bot.cogs.items()]
        loaded_matching_name = [(f'{n} - cogs.{c}', c) for n, c in loaded if (n.lower().startswith(name) or c.startswith(name))]
        if loaded_matching_name:
            await i.send_choices([SlashCommandOptionChoice(n, c) for n, c in loaded_matching_name])
        else:
            await i.send_choices(
                [
                    SlashCommandOptionChoice('There is no loaded extension with this name.', '__no_loaded_extension_with_this_name__')
                ]
            )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(DevCommands(bot))
