import discord
from discord import Embed, Button, ButtonStyle
import i18n

from Database.models import GuildData


async def build_drop_embed(guild_id: int) -> Embed:
	local: str = (await GuildData(guild_id).load()).language
	embed = Embed(
		title=f'`        {i18n.t("drop.title", locale=local)}        `',
		color=0x2f3136
	)
	embed.set_image(url='https://github.com/DevSkyOne/Drops/raw/main/assets/present.png')
	embed.set_footer(text='© 2023 DropBot')
	return embed


async def build_drop_embed_opened(user: discord.User, value: str, guild_id: int) -> Embed:
	local: str = (await GuildData(guild_id).load()).language
	embed = Embed(
		title=f'`        {i18n.t("drop.opened.title", locale=local)}        `',
		color=0x2f3136
	)
	embed.add_field(name=i18n.t('drop.opened.field', locale=local), value=i18n.t('drop.opened.value', user=user.mention,
	                                                                             value=value, locale=local))
	embed.set_footer(text='© 2023 DropBot')
	return embed


async def drop_in_channel(channel: discord.TextChannel) -> discord.Message:
	local: str = (await GuildData(channel.guild.id).load()).language
	return await channel.send(embed=(await build_drop_embed(channel.guild.id)),
	                          components=[[Button(label=f'{i18n.t("drop.open", locale=local)}',
	                                              style=ButtonStyle.green, custom_id='drop:open')]])
