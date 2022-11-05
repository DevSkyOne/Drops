from discord.ext import commands


class DropCommand(commands.Cog):
	def __init__(self, bot) -> None:
		self.bot: commands.Bot = bot


def setup(bot: commands.Bot) -> None:
	bot.add_cog(DropCommand(bot))
