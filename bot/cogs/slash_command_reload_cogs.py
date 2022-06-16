from loguru import logger
from discord.ext import commands
from discord.embeds import Embed
from discord.commands import SlashCommandGroup

from utils.helper import devGuildID


class ReloadCogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    reload_group = SlashCommandGroup("reload", "reload parts of the bot", checks=[commands.is_owner().predicate])

    @reload_group.command(description="Reloads GitHub's Data")
    async def github(self, ctx):
        logger.debug(f"trying to update github data command called by {ctx.author.id}")
        if ctx.author.id == 338947895665360898:
            try:
                from utils.github_api import DataHandler
                dh = DataHandler(update=False)
                dh.update_data()
                await ctx.send(
                    embeds=[Embed(
                        title="Successfully Updated Github data",
                        description="\u200b",
                        colour=int("00ff00", 16)
                    )]
                )
            except BaseException as e:
                logger.warning(e)
                await ctx.send(
                    embeds=[Embed(
                        title="Updating Local cache failed",
                        description="\u200b",
                        colour=int("ff0000", 16)
                    )]
                )
        else:
            await ctx.send(
                embeds=[Embed(
                    title="You dont have permissions to update GitHub data",
                    description="\u200b",
                    colour=int("ff0000", 16)
                )]
            )


def setup(bot):
    bot.add_cog(ReloadCogs(bot))
