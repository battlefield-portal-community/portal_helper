import os
import random

from discord.commands import slash_command, Option
from discord.ext import commands
from discord.embeds import Embed

from utils.helper import devGuildID


class ToolsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="tools", guild_ids=[devGuildID] if os.getenv("PD_DEVELOPMENT") == "True" else None)
    async def tools(self, ctx, hidden: Option(bool, "If set to true only you can see it", required=False)):
        fields = [{
            "name": "BF2042-Portal-Extensions",
            "value": "Extension to add various QOL features to portal's logic editor",
            "url": "https://github.com/LennardF1989/BF2042-Portal-Extensions",
            "user_id": 182574451366428672
        }, {
            "name": "Portal-unleashed",
            "value": "Chrome extension allowing you to make your Portal Experience directly in "
                     "pseudo-Javascript from a VSCode editor in your browser",
            "url": "https://github.com/Ludonope/BFPortalUnleashed",
            "user_id": 145955873913700352
        }, {
            "name": "Game Tools",
            "value": "Community Network aims to provide public tools for different games. Starting with Battlefield, "
                     "we are bringing back online concurrent player stats, as well as personal stats and much more in"
                     " future",
            "url": "https://gametools.network/",
            "user_id": 140391046822494208

        }, {
            "name": "Battlefield Portal Blocks",
            "value": "A repository of some useful Portal Rule Editor Blocks",
            "url": "https://github.com/Andygmb/Battlefield-Portal-Blocks",
            "user_id": 152173878376923136
        }, {
            "name": "Portal Helper",
            "value": "This Bot which gives you access to various commands to help with portal",
            "url": "https://github.com/p0lygun/portal-docs-bot",
            "user_id": 338947895665360898
        }]
        thumbnail_url = "https://cdn.discordapp.com/attachments/" \
                        "908104736455155762/912999248910495784/Animation_logo_discord.gif"
        embed = Embed(
            title="By the Community For the Community",
            url="https://bfportal.gg/",
            description="**A list of tools/resources made by community**\n\n" +
                        "\n\n".join(
                            [
                                f'**[{i["name"]}]({i["url"]})**\n{i["value"]}\nMaintained by <@{i["user_id"]}>'
                                for i in fields
                            ]
                        ),
            color=int(random.choice(self.bot.colors), 16),
        )
        embed.set_thumbnail(url=thumbnail_url)
        await ctx.respond(
            embeds=[embed], ephemeral=hidden
        )


def setup(bot):
    bot.add_cog(ToolsCog(bot))
