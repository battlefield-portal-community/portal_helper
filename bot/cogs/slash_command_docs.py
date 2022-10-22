import os
import random

import discord
from discord.commands import slash_command, Option
from discord.embeds import Embed
from discord.ext import commands, pages
from loguru import logger
from rapidfuzz import fuzz
import re
from utils.github_api import DataHandler, CleanDoc
from utils.helper import devGuildID, COLORS

dh = DataHandler()
dh.load_data()


class RuleBlockPages:

    def __init__(self, clean_doc: CleanDoc):

        self.event_groups = ["Rule", "OnGoing", "OnPlayer", "OnCapture", "OnMCOM", "OnGameMode", "OnVehicle"]
        self.options = {"Description": ''}
        summary = clean_doc['summary'][220:]
        re_groups = list(re.finditer(r"^\*\*.*\*\*$", summary, flags=re.MULTILINE))
        re_groups_len = len(re_groups)
        for index, event in enumerate(re_groups):
            if index != re_groups_len - 1:
                desc = summary[event.end():re_groups[index + 1].start() - 1]
            else:
                desc = summary[event.end():]
            self.options[event.group().replace("*", '')] = desc

        self.pages = [
            Embed(
                title="Rule",
                description=clean_doc['summary'][0:184]
            ),
            Embed(
                title="OnGoing Events",
                description=self.options['Ongoing']
            ),

        ]
        self.pages[0].set_image(
            url="https://raw.githubusercontent.com/battlefield-portal-community/Image-CDN/main/portal_blocks/Rule.png"
        )

        for event in self.event_groups[2:]:
            embed = Embed(
                title=f"{event.replace('On','', 1)} Events"
            )
            [
                embed.add_field(
                    name=local_event,
                    value=value,
                    inline=False
                ) for local_event, value in self.options.items() if local_event.startswith(event)
            ]
            if event == "OnPlayer":
                for _ in ["OnMandown", "OnRevived"]:
                    embed.add_field(
                        name=_,
                        value=self.options[_],
                        inline=False
                    )
            self.pages.append(embed)


async def rule_block_pagination(ctx: discord.ApplicationContext):
    rule_block_pages = RuleBlockPages(dh.get_doc("Rule"))
    page_groups = [
        pages.PageGroup(
            pages=[page],
            label=f"{option} Events",
        ) for option, page in zip(rule_block_pages.event_groups, rule_block_pages.pages)
    ]
    paginator = pages.Paginator(
        pages=page_groups,
        show_menu=True,
        menu_placeholder="Choose Event Type",
        show_disabled=False,
        show_indicator=False,
        timeout=None,
    )
    await paginator.respond(ctx.interaction, ephemeral=False)


def make_bold(text):
    content_final = ""
    for word in text.split(" "):
        if word.isupper():
            content_final += f"**{word}** "
        else:
            content_final += f"{word} "
    return content_final


def get_autocomplete_blocks(ctx: discord.AutocompleteContext | str, closest_match: bool = False) -> list | str:
    """
    Returns a list of 25 elements, sorted by highest fuzz.ratio.

    :param ctx: block name
    :param closest_match: only Returns the closest match
    :return: list
    """
    ratio_list = [(i, fuzz.partial_ratio((ctx if closest_match else ctx.value), i)) for i in dh.docs_dict.keys()]
    blocks = [i[0] for i in sorted(ratio_list, key=lambda x: x[1], reverse=True)][0:(1 if closest_match else 25)]
    if closest_match:
        return blocks[0]
    return blocks


def make_embed(block_name: str) -> discord.Embed:
    """
    Parses data returned by GitHub Api and returns an embed
    :param block_name: str
    :return: discord.Embed
    """
    image_url = f"https://raw.githubusercontent.com/battlefield-portal-community/Image-CDN/main/portal_blocks/{block_name}.png"
    if block_name == "all":
        # todo: Show Complete list of all blocks
        raise NotImplementedError("command to get all blocks not implemented yet")
        # return special_embeds("all")
    elif block_name in dh.docs_dict.keys():
        doc = dh.get_doc(str(block_name))
    else:
        closet_match = get_autocomplete_blocks(block_name, closest_match=True)
        if closet_match != "rule":
            doc = dh.get_doc(closet_match)
        else:
            raise ValueError(f"Unknown Block {block_name}")

    embed_fields = []
    if 'inputs' in doc.keys():
        embed_fields.append({
            "name": "Inputs",
            "value": "\n".join(doc['inputs']),
            "inline": False
        })
    if 'output' in doc.keys():
        embed_fields.append({
            "name": "Output",
            "value": "\n".join(doc['output'])
        })
    embed = Embed(
        title=doc['block'],
        url=f"https://docs.bfportal.gg/docs/blocks/{doc['block']}",
        description=doc['summary'],
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
            if block_name.lower() != "rule":
                await ctx.respond(
                    embeds=[make_embed(block_name)],
                    ephemeral=hidden
                )
            else:
                await rule_block_pagination(ctx)
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
            logger.warning(f"Error {e} with {block_name} {get_autocomplete_blocks(block_name, closest_match=True)}")
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
