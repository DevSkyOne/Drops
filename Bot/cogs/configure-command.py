import discord
import i18n
from discord import Localizations, SlashCommandOption, SlashCommandOptionChoice, ApplicationCommandInteraction
from discord.ext import commands

from Database.models import GuildData


class ConfigureCommand(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.slash_command(
		base_name='configure',
		base_name_localizations=Localizations(german='konfigurieren', french='configurer'),
		name='language',
		description='Select the language of the bot',
		description_localizations=Localizations(german='Wähle die Sprache des Bots', french='Sélectionnez la langue du bot'),
		default_required_permissions=discord.Permissions(administrator=True),
		options=[
			SlashCommandOption(
				name='language',
				name_localizations=Localizations(german='sprache', french='langue'),
				description='The language of the bot',
				description_localizations=Localizations(german='Die Sprache des Bots', french='La langue du bot'),
				option_type=str,
				required=True,
				choices=[
					SlashCommandOptionChoice(
						name='English',
						name_localizations=Localizations(german='Englisch', french='Anglais'),
						value='en'
					),
					SlashCommandOptionChoice(
						name='German',
						name_localizations=Localizations(german='Deutsch', french='Allemand'),
						value='de'
					)
				]
			)
		]
	)
	async def language(self, ctx: ApplicationCommandInteraction, language: str):
		guild_data = await GuildData(ctx.guild_id).load()
		guild_data.language = language
		await guild_data.save()
		await ctx.respond(f'{i18n.t("configure.language.success", language=language, locale=language)}', hidden=True)


def setup(bot):
	bot.add_cog(ConfigureCommand(bot))
