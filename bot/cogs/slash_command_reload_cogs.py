from loguru import logger
from discord.commands import slash_command, permissions, Option
from discord.ext import commands
from discord.embeds import Embed

from utils.helper import devGuildID


class ReloadCogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="reload_cogs", guild_ids=[devGuildID], default_permission=False)
    @permissions.is_owner()
    async def reload_cogs(
            self,
            ctx,
            module: Option(str, "Name of the module to reload")
    ):
        f"""
        Reload a gives extension to enable Hot reload
    
        :param ctx: context 
        :param module: name of the module must be one of {self.bot.cogs_list}
        :return: None
        """
        if module not in self.bot.cogs_list:
            embed = Embed(
                    title=":red_circle: :red_circle: Command Failed :red_circle: :red_circle: ",
                    description=f"Invalid cog {module} valid cogs are :-",
                    color=int("ff0000", 16)
                )

            await ctx.respond(embeds=[embed])
            return
        elif module == "bot.cogs.slash_command_reload_cogs":
            await ctx.respond(embeds=[
                Embed(
                    title="Wow really!!! ?",
                    description=f"U can't unload the un-loader itself LOL",
                    color=int("ff0000", 16)
                )],
            )
            return

        logger.debug(f"Trying to reload cog {module}")
        try:
            self.bot.unload_extension(module)
        except BaseException as e:
            logger.critical(f"Error {e} happened when unloading cog {module}")
            await ctx.respond(embeds=[
                Embed(
                    title=f"Error Happened when unloading cog {module}",
                    description=f"{e}",
                    color=int("ff0000", 16)
                )]
            )

        try:
            self.bot.load_extension(module)
        except BaseException as e:
            logger.critical(f"Error {e} happened when loading cog {module}")
            await ctx.respond(embeds=[
                Embed(
                    title=f"Error Happened when loading cog {module}",
                    description=f"{e}",
                    color=int("ff0000", 16)
                )]
            )

        logger.debug(f"Successfully reloaded cog {module}")

        await ctx.respond(embeds=[
            Embed(
                title=f"Successfully reloaded cog {module}",
                description=f":white_check_mark:",
            )]
        )

    @slash_command(name="reload_github", guild_ids=[devGuildID], default_permission=False)
    @permissions.is_owner()
    async def reload(self, ctx):
        if ctx.author.user.id == "338947895665360898":
            try:
                from utils.github_api import DataHandler
                dh = DataHandler(update=False)
                dh.update_data()
                await ctx.send(
                    embeds=[Embed(
                        title="Successfully Updated sha-mapping",
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


def setup(bot):
    bot.add_cog(ReloadCogs(bot))
