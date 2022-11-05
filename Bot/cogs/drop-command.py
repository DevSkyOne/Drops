import discord
from discord import Localizations, ApplicationCommandInteraction, SlashCommandOption
from discord.ext import commands

from Bot.data.dropbuilder import drop_in_channel, build_drop_embed_opened

drops = {}


class DropCommand(commands.Cog):
	def __init__(self, bot) -> None:
		self.bot: commands.Bot = bot

	@commands.Cog.slash_command(
		name='drop',
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
		await ctx.respond('Drop in progress...', hidden=True)
		message = await drop_in_channel(ctx.channel)
		drops[message.id] = {
			'type': droptype,
			'value': dropvalue,
			'receiver': None
		}

	@commands.Cog.on_click('drop:open')
	async def open_drop(self, ctx: discord.ComponentInteraction, _) -> None:
		if drops.get(ctx.message.id).get('receiver') is None:
			drops[ctx.message.id] = {
				'type': drops.get(ctx.message.id).get('type'),
				'value': drops.get(ctx.message.id).get('value'),
				'receiver': ctx.user.id
			}
			await ctx.message.edit(
				embeds=[build_drop_embed_opened(ctx.author, value=drops.get(ctx.message.id).get('type'))],
				components=[])
			await ctx.respond(f'You opened the drop! {drops.get(ctx.message.id).get("value")}', hidden=True)
		else:
			await ctx.respond('The drop is already open!', hidden=True)


def setup(bot: commands.Bot) -> None:
	bot.add_cog(DropCommand(bot))
