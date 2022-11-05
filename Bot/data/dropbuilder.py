from discord import Embed
import i18n


def build_drop_embed() -> Embed:
	embed = Embed(
		title=f'`        {i18n.t("drop.title")}        `',
		color=0x2f3136
	)
	embed.set_image(url='https://github.com/DevSkyOne/Drops/raw/main/assets/present.png')
	embed.set_footer(text='© 2022 DropBot')
	return embed
