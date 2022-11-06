import discord
import i18n
from discord import Localizations, SlashCommandOption, SlashCommandOptionChoice, ApplicationCommandInteraction
from discord.ext import commands

from Database.models import GuildData, PresetData


class ConfigurePresetsCommand(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.slash_command(
		base_name='configure',
		base_name_localizations=Localizations(german='konfigurieren', french='configurer'),
		name='preset',
		description='Configure a preset',
		description_localizations=Localizations(german='Konfiguriere ein Preset', french='Configurer un préréglage'),
		default_required_permissions=discord.Permissions(administrator=True),
		options=[
			SlashCommandOption(
				name='name',
				name_localizations=Localizations(german='name', french='nom'),
				description='The name of the preset',
				description_localizations=Localizations(german='Der Name des Presets', french='Le nom du préréglage'),
				option_type=str,
				required=True
			),
			SlashCommandOption(
				name='description',
				name_localizations=Localizations(german='beschreibung', french='description'),
				description='The description of the preset',
				description_localizations=Localizations(german='Die Beschreibung des Presets', french='La description du préréglage'),
				option_type=str,
				required=True
			),
			SlashCommandOption(
				name='value',
				name_localizations=Localizations(german='wert', french='valeur'),
				description='The value of the preset',
				description_localizations=Localizations(german='Der Wert des Presets', french='La valeur du préréglage'),
				option_type=str,
				required=False
			)
		]
	)
	async def preset(self, ctx: ApplicationCommandInteraction, name: str, description: str, value: str = None):
		guild_data = await GuildData(ctx.guild_id).load()
		preset_data = await PresetData(guild_id=ctx.guild_id).load()
		preset_data.name = name
		preset_data.description = description
		preset_data.value = value
		guild_data.presets.append(preset_data)
		await guild_data.save()
		await ctx.respond(f'{i18n.t("configure.preset.success", language=guild_data.language)}', hidden=True)


def setup(bot):
	bot.add_cog(ConfigurePresetsCommand(bot))
