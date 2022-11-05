import discord
from discord import Embed, Button, ButtonStyle
import i18n


def build_drop_embed() -> Embed:
	embed = Embed(
		title=f'`        {i18n.t("drop.title")}        `',
		color=0x2f3136
	)
	embed.set_image(url='https://github.com/DevSkyOne/Drops/raw/main/assets/present.png')
	embed.set_footer(text='© 2022 DropBot')
	return embed


def build_drop_embed_opened(user: discord.User, value: str) -> Embed:
	embed = Embed(
		title=f'`        {i18n.t("drop.opened.title")}        `',
		color=0x2f3136
	)
	embed.add_field(name=i18n.t('drop.opened.field'), value=i18n.t('drop.opened.value', user=user.mention, value=value))
	embed.set_footer(text='© 2022 DropBot')
	return embed


async def drop_in_channel(channel: discord.TextChannel) -> discord.Message:
	return await channel.send(embed=build_drop_embed(), components=[[Button(label=f'{i18n.t("drop.open")}',
	                                                                style=ButtonStyle.green, custom_id='drop:open')]])
