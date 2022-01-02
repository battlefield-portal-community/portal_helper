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

    @slash_command(
        name="experience_info",
        guild_ids=[devGuildID] if os.getenv("PD_DEVELOPMENT") == "True" else None,
        description="Shows info about portal experiences"
    )
    async def make_url_embed(self, ctx,
                             url: Option(str, "Url of the experience", required=False),
                             playground_id: Option(str, "PlaygroundID of the experience", required=False)
                             ):
        if url:
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
        else:
            playground_id = playground_id
            url = f"https://portal.battlefield.com/experience/mode/game-mode?playgroundId={playground_id}"
        # make gametools API call to get name and desc
        resp_json = requests.get(
            url=f"https://api.gametools.network/bf2042/playground/?playgroundid={playground_id}"
        ).json()

        if "errors" in resp_json.keys():
            logger.info(
                f"Invalid URL with wrong playgroundID {{{playground_id}}} "
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

        experience_info = resp_json["validatedPlayground"]
        embed = Embed(
            title=experience_info["playgroundName"].capitalize(),
            description=f"**{experience_info['playgroundDescription']}**",
            color=get_random_color(),
            url=url
        )

        embed.add_field(
            name="Last Updated",
            value=f"<t:{experience_info['updatedAt']['seconds']}>",
        )
        embed.add_field(
            name="Created At",
            value=f"<t:{experience_info['createdAt']['seconds']}>",
        )
        embed.add_field(
            name="\u200B",
            value="\u200B"
        )

        embed.add_field(
            name="Type",
            value=experience_info["blueprintType"],
        )
        embed.add_field(
            name="Max players",
            value=f"{experience_info['mapRotation']['maps'][0]['gameSize']}".strip(),
            inline=True
        )
        embed.add_field(
            name="\u200B",
            value="\u200B"
        )

        embed.add_field(
            name="PlaygroundID",
            value=experience_info["playgroundId"],
            inline=False
        )

        tag_data = resp_json["tag"]
        tags = [f'`{i["values"][0]["readableSettingName"]}`' for i in tag_data]
        embed.add_field(
            name="Tags",
            value=" ".join(tags)
        )
        embed.set_thumbnail(
            url=f"{experience_info['mapRotation']['maps'][0]['image']}"
        )

        embed.set_footer(
            text=f"Experience Made by {experience_info['owner']['name']}",
            icon_url=experience_info['owner']['avatar']
        )

        # send the embed :)
        await ctx.respond(embeds=[embed])


def setup(bot):
    bot.add_cog(ExperienceUrlEmbed(bot))
