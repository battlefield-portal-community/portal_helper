import os
import random

import discord
from rapidfuzz import fuzz
from discord.commands import slash_command, Option
from discord.ext import commands
from discord.embeds import Embed
from loguru import logger

from utils.helper import devGuildID, COLORS
from utils.github_api import DataHandler

dh = DataHandler()
dh.load_data()


def special_embeds(block_name):
    if block_name == "rule":
        doc_list = [i for i in dh.get_doc("rule").split("\n") if i != ""]

        fields_list = []
        for i in range(4, len(doc_list) - 1, 2):
            fields_list.append({
                "name": doc_list[i],
                "value": doc_list[i + 1],
                "inline": False
            })

        embed = Embed(
            title=make_bold(doc_list[0]),
            url=f"https://docs.bfportal.gg/docs/blocks/{doc_list[0]}",
            description=doc_list[1] + f"\n**{doc_list[3]}**",
            color=random.choice(COLORS),
        )
        for field in fields_list:
            embed.add_field(**field)
        return embed

    if block_name == "all":
        pass


def make_bold(text):
    content_final = ""
    for word in text.split(" "):
        if word.isupper():
            content_final += f"**{word}** "
        else:
            content_final += f"{word} "
    return content_final


def get_autocomplete_blocks(ctx: discord.AutocompleteContext) -> list:
    """
    Returns a list of 25 elements, sorted by highest fuzz.ratio

    :param ctx:
    :return:
    """
    ratio_list = [(i, fuzz.ratio(ctx.value.lower(), i)) for i in dh.docs_dict.keys()]
    ratio_list.sort(key=lambda x: x[1], reverse=True)
    autocomplete_list = [dh.docs_dict[i[0]][-1] for i in ratio_list[0:25]]
    # autocomplete_list = [value[-1] for key, value in dh.docs_dict.items() if key.startswith(ctx.value.lower())][0:25]
    return autocomplete_list


def get_closest_match(block: str) -> list:
    """
    same as get_autocomplete_blocks but for internal use
    :param block: str, block name
    :return:
    """
    ratio_list = [(i, fuzz.ratio(block, i)) for i in dh.docs_dict.keys()]
    ratio_list.sort(key=lambda x: x[1], reverse=True)
    return ratio_list[0][0]


def make_embed(block_name: str) -> discord.Embed:
    """
    Parses data returned by Github Api and returns an embed
    :param block_name: str
    :return: discord.Embed
    """
    image_url = f"https://portal-helper-block-images.s3.amazonaws.com/blocks_images/{block_name}.png"
    block_name = block_name.lower()
    if block_name == "all":
        # todo: Show Complete list of all blocks
        raise NotImplementedError("command to get all blocks not implemented yet")
        # return special_embeds("all")
    elif block_name == "rule":
        return special_embeds("rule")
    elif block_name in dh.docs_dict.keys():
        doc = dh.get_doc(str(block_name))
    else:
        closet_match = get_closest_match(block_name)
        if closet_match != "rule":
            doc = dh.get_doc(closet_match)
        else:
            return special_embeds("rule")
    doc_list = [i for i in doc.split("\n") if i != ""]
    output = ''
    inputs = ''
    title = doc_list[0]
    if "Inputs" in doc_list:
        content = doc_list[1:doc_list.index("Inputs")][0]
    else:
        content = doc_list[1:][0]
    if "Output" in doc_list:
        if "Inputs" in doc_list:
            inputs = doc_list[doc_list.index("Inputs") + 1:doc_list.index("Output")]
        output = doc_list[doc_list.index("Output") + 1:]
    else:
        if "Inputs" in doc_list:
            inputs = doc_list[doc_list.index("Inputs") + 1:]

    inputs = " ".join(inputs)
    output = " ".join(output)
    content = make_bold(content)
    notes = ''
    if "Notes" in inputs:
        tmp = inputs.split("Notes")
        notes = tmp[1]
        inputs = tmp[0]
    if "Notes" in output:
        tmp = output.split("Notes")
        notes = tmp[1]
        output = tmp[0]
    url = title.replace(" ", "")
    embed_fields = []
    if inputs:
        embed_fields.append({
            "name": "Inputs",
            "value": inputs,
            "inline": False
        })
    if output:
        embed_fields.append({
            "name": "Output",
            "value": output
        })
    if notes:
        embed_fields.append({
            "name": "Notes",
            "value": notes,
            "inline": False
        })
    embed = Embed(
        title=title,
        url=f"https://docs.bfportal.gg/docs/blocks/{url}",
        description=content,
        color=random.choice(COLORS),
    )
    for field in embed_fields:
        embed.add_field(**field)
    embed.set_image(url=image_url)
    return embed


class DocumentationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="d",
        guild_ids=[devGuildID] if os.getenv("PD_DEVELOPMENT") == "True" else None,
        description="Returns the documentation of a block used in portal's rule editor"
    )
    async def docs(self,
                   ctx: discord.ApplicationContext,
                   block_name: Option(str, "Name of the block",
                                      autocomplete=discord.utils.basic_autocomplete(get_autocomplete_blocks)),
                   hidden: Option(bool, "If this is set to true only you can see the output", required=False)
                   ):
        try:
            embed = make_embed(block_name)
            await ctx.respond(embeds=[embed], ephemeral=hidden)
        except NotImplementedError as e:
            logger.warning(e)
            await ctx.respond(
                embeds=[Embed(
                    title="Not Yet Implemented",
                    description=f"Command {block_name}",
                    colour=int("ff0000", 16)
                )], ephemeral=hidden,
            )
        except BaseException as e:
            logger.warning(f"Error {e} with {block_name} {get_closest_match(block_name)}")
            await ctx.respond(
                embeds=[Embed(
                    title=f"Error getting docs for {block_name}",
                    description="\u200b",
                    colour=int("ff0000", 16),
                )], ephemeral=hidden
            )
        except ValueError as e:
            logger.critical(e)
            await ctx.respond(
                embeds=[Embed(
                    title=f"Error getting docs for {block_name}",
                    description="\u200b",
                    colour=int("ff0000", 16),
                )], ephemeral=hidden
            )


def setup(bot):
    bot.add_cog(DocumentationCog(bot))
