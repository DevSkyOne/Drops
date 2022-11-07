import discord
import i18n
from discord import Localizations, ApplicationCommandInteraction, SlashCommandOption, AutocompleteInteraction, \
	SlashCommandOptionChoice
from discord.ext import commands

from Bot.data.dropbuilder import drop_in_channel, build_drop_embed_opened
from Database.models import GuildData, PresetData

drops = {}


class DropCommand(commands.Cog):
	def __init__(self, bot) -> None:
		self.bot: commands.Bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print(f'Bot is on {len(self.bot.guilds)} guilds')
		for guild in self.bot.guilds:
			print(f'Guild: {guild.name} ({guild.id})')

	@commands.Cog.slash_command(
		base_name='drop',
		name='now',
		description='drops a present',
		description_localizations=Localizations(german='Droppt ein Geschenk', french='droppe un cadeau'),
		default_required_permissions=discord.Permissions(administrator=True),
		options=[
			SlashCommandOption(
				name='droptype',
				description='The type of the drop (e.g. "1 month nitro")',
				option_type=str,
				required=True
			),
			SlashCommandOption(
				name='dropvalue',
				description='The value of the drop (e.g. link to nitro)',
				option_type=str,
				required=True
			)
		]
	)
	async def drop(self, ctx: ApplicationCommandInteraction, droptype: str, dropvalue: str) -> None:
		locale: str = (await GuildData(ctx.guild_id).load()).language
		await ctx.respond(f'{i18n.t("drop.in_progress", locale=locale)}', hidden=True)
		message = await drop_in_channel(ctx.channel)
		drops[message.id] = {
			'type': droptype,
			'value': dropvalue,
			'receiver': None
		}

	@commands.Cog.slash_command(
		base_name='drop',
		name='preset',
		description='drops a present',
		description_localizations=Localizations(german='Droppt ein Geschenk', french='droppe un cadeau'),
		default_required_permissions=discord.Permissions(administrator=True),
		options=[
			SlashCommandOption(
				name='preset',
				name_localizations=Localizations(german='preset', french='préréglage'),
				description='The preset to use',
				description_localizations=Localizations(german='Das zu verwendende Preset', french='Le préréglage à utiliser'),
				option_type=str,
				required=True,
				autocomplete=True
			),
			SlashCommandOption(
				name='value',
				description='The value of the drop (e.g. link to nitro)',
				option_type=str,
				required=False
			)
		]
	)
	async def drop_preset(self, ctx: ApplicationCommandInteraction, preset: str, value: str = None) -> None:
		guild_data = await GuildData(ctx.guild_id).load()
		preset_data = [preset_d for preset_d in guild_data.presets if preset_d.name == preset]
		if len(preset_data) == 0:
			await ctx.respond(f'{i18n.t("preset.not_found", preset=preset, locale=guild_data.language)}', hidden=True)
			return
		preset_data: PresetData | list = preset_data[0]
		if value is None and preset_data.value is None:
			await ctx.respond(f'{i18n.t("preset.no_value", preset=preset, locale=guild_data.language)}', hidden=True)
			return
		await ctx.respond(f'{i18n.t("drop.in_progress", locale=guild_data.language)}', hidden=True)
		message = await drop_in_channel(ctx.channel)
		drops[message.id] = {
			'type': preset_data.description,
			'value': preset_data.value if value is None else value,
			'receiver': None
		}

	@drop_preset.autocomplete_callback
	async def drop_preset_autocomplete(self, ctx: AutocompleteInteraction, preset: str, value: str = None) -> None:
		guild_data = await GuildData(ctx.guild_id).load()
		presets = [preset_d for preset_d in guild_data.presets if (preset_d.description.startswith(preset) if preset is not None else preset_d.description)]
		return await ctx.send_choices([SlashCommandOptionChoice(name=preset_d.description, value=preset_d.name) for preset_d in presets])

	@commands.Cog.on_click('drop:open')
	async def open_drop(self, ctx: discord.ComponentInteraction, _) -> None:
		locale: str = (await GuildData(ctx.guild_id).load()).language
		if drops.get(ctx.message.id).get('receiver') is None:
			drops[ctx.message.id] = {
				'type': drops.get(ctx.message.id).get('type'),
				'value': drops.get(ctx.message.id).get('value'),
				'receiver': ctx.user.id
			}
			await ctx.message.edit(
				embeds=[await build_drop_embed_opened(ctx.author, value=drops.get(ctx.message.id).get('type'), guild_id=ctx.guild_id)],
				components=[])
			await ctx.respond(f'{i18n.t("drop.opened.claimed", value=drops.get(ctx.message.id).get("value"), locale=locale)}',
			                  hidden=True)
		else:
			await ctx.respond(f'{i18n.t("drop.opened.failed", locale=locale)}', hidden=True)


def setup(bot: commands.Bot) -> None:
	bot.add_cog(DropCommand(bot))
