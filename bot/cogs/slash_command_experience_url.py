import os
from urllib.parse import urlparse

from discord.commands import slash_command, Option
from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Colour
import requests
from loguru import logger

from utils.helper import devGuildID, get_random_color


class ExperienceUrlEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="experience_embed", guild_ids=[devGuildID] if os.getenv("PD_DEVELOPMENT") == "True" else None)
    async def make_url_embed(self, ctx,
                             url: Option(str, "Url of the experience")
                             ):
        parsed_url = urlparse(url)
        valid_url = True
        # check for valid url
        # a valid parsed url is like
        # ParseResult(scheme='https', netloc='portal.battlefield.com', path='/experience/rules', params='',
        # query='playgroundId=a40094d0-69a3-11ec-a77f-970dc4ce1096', fragment='')

        if parsed_url.netloc != "portal.battlefield.com":
            valid_url = False
        elif parsed_url.query.split("=")[0] != "playgroundId":
            valid_url = False

        if not valid_url:
            logger.info(f"Invalid URL {{{url}}} sent by {ctx.author}:{ctx.author.id}")
            await ctx.respond(embeds=[
                Embed(
                    title="Invalid Url",
                    description="\u200b",
                    color=Colour.red()
                )
            ], ephemeral=True)
            return
        playground_id = parsed_url.query.split("=")[1]
        # make gametools API call to get name and desc
        resp_json = requests.get(
            url=f"https://api.gametools.network/bf2042/playground/?playgroundid={playground_id}"
        ).json()

        if "errors" in resp_json.keys():
            logger.info(
                f"Invalid URL with wrong playgroundID {{{url}}} "
                f"sent by {ctx.author}:{ctx.author.id}"
            )
            await ctx.respond(embeds=[
                Embed(
                    title="Invalid PlaygroundID",
                    description="\u200b",
                    color=Colour.red()
                )
            ], ephemeral=True)
            return

        experience_info = resp_json["naming"]
        embed = Embed(
            title=experience_info["playgroundName"],
            description=experience_info["playgroundDescription"],
            color=get_random_color(),
            url=url
        )
        embed.add_field(
            name="PlaygroundID",
            value=experience_info["playgroundId"]
        )
        embed.add_field(
            name="Type",
            value=experience_info["type"]
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/908104736455155762/908106030892851200/bf_portal_logo_bc.png"
        )

        # send the embed :)
        await ctx.respond(embeds=[embed])


def setup(bot):
    bot.add_cog(ExperienceUrlEmbed(bot))
