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
        embed = Embed(
            title="By the Community For the Community",
            url="https://bfportal.gg/",
            description="**A list of tools/resources made by community**\u200B",
            color=int(random.choice(self.bot.colors), 16),
        )
        spacer = {
            "name": "\u200B",
            "value": "\u200B"
        }
        fields = [
            {
                "name": "BF2042-Portal-Extensions\n",
                "value": "Extension to add various QOL features to portal's logic editor\n"
                         "[github.com/LennardF1989/BF2042-Portal-Extensions]("
                         "https://github.com/LennardF1989/BF2042-Portal-Extensions)\nMade by [ "
                         "LennardF1989#3733 ]",
                "inline": False
            },
            {
                "name": "Portal-unleashed",
                "value": "\nChrome extension allowing you to make your Portal Experience directly in "
                         "pseudo-Javascript from a VSCode editor in your browser\n Download "
                         "from:- [github.com/Ludonope/BFPortalUnleashed](https://github.com/Ludonope/BFPortalUnleashed)\n"
                         "Made by [ ludonope#4197 ]\u200B",
                "inline": False
            },
            {
                "name": "Battlefield Portal Blocks",
                "value": "A repository of some useful Portal Rule Editor Blocks\n["
                         "github.com/Andygmb/Battlefield-Portal-Blocks]( "
                         "https://github.com/Andygmb/Battlefield-Portal-Blocks) \nmaintained by [ andy#0743 ]",
                "inline": False
            }
        ]
        footer_text = "And lastly this bot which was made by [ gala#8316 ] " \
                      "\nMaintained at\n https://github.com/p0lygun/portal-docs-bot"
        thumbnail_url = "https://cdn.discordapp.com/attachments/" \
                        "908104736455155762/912999248910495784/Animation_logo_discord.gif"

        for i in fields:
            embed.add_field(**i)
            embed.add_field(**spacer)

        embed.set_thumbnail(url=thumbnail_url)
        embed.set_footer(text=footer_text)

        await ctx.respond(
            embeds=[embed], ephemeral=hidden
        )


def setup(bot):
    bot.add_cog(ToolsCog(bot))

