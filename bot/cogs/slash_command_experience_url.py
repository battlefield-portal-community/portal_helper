import os
from typing import Union
from urllib.parse import urlparse

from discord.commands import slash_command, Option
from discord.ext import commands

from discord.embeds import Embed
from discord.colour import Colour
import requests
from loguru import logger

from utils.helper import devGuildID, get_random_color


def get_playground_id(url: str) -> Union[bool, str]:
    """
    Checks if a url is a good portal url
    :param url:
    :return: playgroundID if True else False
    """
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
        return False
    return parsed_url.query.split("=")[1]


def make_embed(playground_id: str = None, experience_code: str = None) -> Union[Embed, bool]:
    """
    Makes Embed from a playground_id
    :param playground_id: playgroundId of a experience
    :param experience_code: Experience Code
    :return: Embed if playground_id is valid, else False
    """
    if playground_id:
        url = f"https://portal.battlefield.com/experience/mode/game-mode?playgroundId={playground_id}"
        request_url = f"https://api.gametools.network/bf2042/playground/?playgroundid={playground_id}&blockydata=false&lang=en-us"
    elif experience_code:
        url = f"https://bfportal.gg/"
        request_url = f"https://api.gametools.network/bf2042/playground/?experiencecode={experience_code.strip()}&blockydata=false&lang=en-us"
    # make gametools API call to get name and desc

    logger.debug(request_url)
    resp_json = requests.get(url = request_url).json()

    if "errors" in resp_json.keys():
        return False

    experience_info = resp_json["validatedPlayground"]
    embed = Embed(
        title=experience_info["playgroundName"].capitalize(),
        description=f"**{experience_info['playgroundDescription']}**",
        color=get_random_color(),
        url=url
    )

    embed.add_field(
        name="Last Updated",
        value=f"> <t:{experience_info['updatedAt']['seconds']}>",
    )
    embed.add_field(
        name="Created At",
        value=f"> <t:{experience_info['createdAt']['seconds']}>",
    )

    if experience_code:
        embed.add_field(
            name="Experience Code",
            value=f"> **{experience_code}**"
        )
    elif playground_id:
        embed.add_field(
            name="Experience URL",
            value=f"> [Open 🔗](https://portal.battlefield.com/experience/rules?playgroundId={playground_id})"
        )
    else:
        embed.add_field(
            name="\u200B",
            value="\u200B"
        )

    xp_type = None

    tag_data = resp_json["tag"]
    tags = []
    for i in tag_data:
        tag_info = i["metadata"]["translations"][0]
        tags.append(f'`{tag_info["localizedText"]}`')
        if tag_info['translationId'] == "ID_ARRIVAL_SERVERTAG_CUSTOM_SCRIPTED":
            xp_type = "Restricted"

    if xp_type is None:
        for mutator in experience_info['mutators']:
            if "WA_XP_Reduced" in mutator['category'].split(','):
                xp_type = "Moderate"

    if xp_type is None:
        xp_type = 'Full'

    embed.add_field(
        name="Progression",
        value=f'> {xp_type}',
    )
    team_composition = experience_info.get('teamComposition', '')
    if team_composition:
        team_composition = f"({'v'.join([str(team['capacity']) for team in team_composition['teams']])})"
    embed.add_field(
        name="Max players",
        value=f"> {experience_info['mapRotation']['maps'][0]['gameSize']} {team_composition}".strip(),
        inline=True
    )
    embed.add_field(
        name="\u200B",
        value="\u200B"
    )

    if playground_id:
        embed.add_field(
            name="PlaygroundID",
            value=f'> {experience_info["playgroundId"]}',
            inline=False
        )
    elif experience_code:
        embed.add_field(
            name="Number of Maps",
            value=f'> {len(experience_info["mapRotation"]["maps"])}',
            inline=False
        )

    embed.add_field(
        name="Tags",
        value="> " + " ".join(tags)
    )
    embed.set_thumbnail(
        url=f"{experience_info['mapRotation']['maps'][0]['image']}"
    )

    if playground_id:
        embed.set_footer(
            text=f"Experience Made by {experience_info['owner']['name']}",
            icon_url=experience_info['owner']['avatar']
        )
    return embed


class ExperienceUrlEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        playground_id = get_playground_id(message.content)
        embed = False
        if playground_id:
            embed = make_embed(playground_id)

        if embed:
            await message.channel.send(embeds=[embed])

    @slash_command(
        name="experience_info",
        guild_ids=[devGuildID] if os.getenv("PD_DEVELOPMENT") == "True" else None,
        description="Shows info about portal experiences"
    )
    async def make_url_embed(self, ctx,
                             input_type: Option(str, "Choose the input type", choices=["Url", "Playground ID", "Experience Code"]),
                             value: Option(str, "Input Value")
                             ):
        url, playground_id, experience_code = None, None, None
        match input_type.lower():
            case "url":
                url = value
            case "playground id":
                playground_id = value
            case "experience code":
                experience_code = value

        logger.debug(f"ExperienceUrlEmbed {url} {playground_id} {experience_code}")
        if url:
            playground_id = get_playground_id(url)
            if not playground_id:
                logger.info(f"Invalid URL {{{url}}} sent by {ctx.author}:{ctx.author.id}")
                await ctx.respond(embeds=[
                    Embed(
                        title="Invalid Url",
                        description="\u200b",
                        color=Colour.red()
                    )
                ], ephemeral=True)
                return
        if playground_id:
            embed = make_embed(playground_id, None)
        elif experience_code:
            embed = make_embed(None, experience_code)

        if not embed:
            logger.info(
                f"Invalid playgroundID {{{playground_id}}} "
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

        # send the embed :)
        await ctx.respond(embeds=[embed])


def setup(bot):
    bot.add_cog(ExperienceUrlEmbed(bot))
