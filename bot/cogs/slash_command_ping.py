import os
import random

from discord.commands import slash_command
from discord.ext import commands
from discord.embeds import Embed

from utils.helper import devGuildID


class PingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="ping",
        guild_ids=[devGuildID]
    )
    async def pinged(self, ctx):
        """
        Shows the ping of the bot
        """
        await ctx.respond(embeds=[Embed(
            title=f"ping {int(self.bot.latency*1000)} ms",
            description="\u200b",
        )])


def setup(bot):
    bot.add_cog(PingCog(bot))
