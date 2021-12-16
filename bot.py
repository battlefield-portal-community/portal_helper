import os
import random
from pathlib import Path

from thefuzz import fuzz
from github_api import DataHandler
from dotenv import load_dotenv
from interactions import Embed
from interactions import Choice, Option, OptionType, Client
import logging
from logging import handlers

load_dotenv()
bot = Client(token=os.getenv("DISCORD_TOKEN"), log_level=logging.CRITICAL)
logging.getLogger("mixin").setLevel(logging.CRITICAL)
for name in ["client", "context", "dispatch", "gateway", "http", "mixin"]:
    ch = handlers.TimedRotatingFileHandler(f"{Path.cwd()}", 'midnight', 1)
    ch.setLevel(logging.DEBUG)
    logging.getLogger(name).addHandler(ch)
    logging.getLogger(name).addHandler(ch)
logger = logging.getLogger("client")
dh = DataHandler(update=False)
dh.load_data()


def make_bold(text):
    content_final = ""
    for word in text.split(" "):
        if word.isupper():
            content_final += f"**{word}** "
        else:
            content_final += f"{word} "
    return content_final


def get_choice_list():
    return [Choice(name=j[1], value=i) for i, j in dh.docs_dict.items()]


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
            color=int(random.choice(colors), 16),
            fields=fields_list
        )
        return embed

    if block_name == "all":
        pass


def make_embed(block_name):
    block_name = str(block_name).lower()
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
        color=int(random.choice(colors), 16),
        footer={"text": "click on title to go to full documentation"},
        fields=embed_fields
    )
    return embed


def get_closest_match(block, l : bool = False):
    ratio_list = [(i, fuzz.ratio(block, i)) for i in dh.docs_dict.keys()]
    ratio_list.sort(key=lambda x: x[1], reverse=True)
    if l:
        return ratio_list
    return ratio_list[0][0]


hidden = Option(
        name="hidden",
        description="If set to true only you can see it :smile:",
        type=OptionType.BOOLEAN,
        required=False
)
colors = ["011C26", "025159", "08A696", "26FFDF", "F26A1B", "FF2C10"]

@bot.event
async def on_ready():
    print("Ready!")


@bot.command(
    name="tools",
    description="A list of tools/resources made by community",
    options=[hidden],
)
async def tools(ctx, hidden: bool= False):
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

    embed_field_list = []
    for i in fields:
        embed_field_list.append(i)
        embed_field_list.append(spacer)

    await ctx.send(
        embeds=[
            Embed(
                title="By the Community For the Community",
                url="https://bfportal.gg/",
                description="**A list of tools/resources made by community**\u200B",
                color=int(random.choice(colors), 16),
                thumbnail={"url": thumbnail_url},
                footer={"text": footer_text},
                fields=[f(i) for i in fields for f in (lambda x: x, lambda x: spacer)]
            )
        ], ephemeral=hidden
    )


@bot.command(name="d", description="Returns Documentation of a block",
             options=[
                 Option(
                     name="block_name",
                     description="Name of the Block. fuzzy search and lowercase search is on",
                     type=OptionType.STRING,
                     autocomplete=True,
                 ), hidden]
             )
async def d(ctx, block_name, hidden: bool = False):
    try:
        embed = make_embed(block_name)
        await ctx.send(embeds=[embed], ephemeral=hidden)
    except NotImplementedError as e:
        logger.warning(e)
        await ctx.send(
            embeds=[Embed(
                title="Not Yet Implemented",
                description=f"Command {block_name}",
                colour=int("ff0000", 16)
            )], ephemeral=hidden,
        )
    except BaseException as e:
        logger.warning(f"Error with {block_name} {get_closest_match(block_name)}")
        await ctx.send(
            embeds=[Embed(
                title=f"Error getting docs for {block_name}",
                description="\u200b",
                colour=int("ff0000", 16),
            )], ephemeral=hidden
        )
        raise
    except ValueError as e:
        logger.critical(e)
        await ctx.send(
            embeds=[Embed(
                title=f"Error getting docs for {block_name}",
                description="\u200b",
                colour=int("ff0000", 16),
            )], ephemeral=hidden
        )


@bot.autocomplete("block_name")
async def autocomplete_block_name(ctx):
    typed = ctx.data.options[0]["value"]
    if ctx.data.options[0]["focused"]:
        if typed == '':
            await ctx.populate(get_choice_list()[0:25])
        else:

            await ctx.populate([
                Choice(name=dh.docs_dict[i[0]][1], value=i[0]) for i in get_closest_match(typed, True)[0:10]
            ])



@bot.command(
    name="reload",
    description="reloads local cache on bot server",
    scope=829265067073339403
)
async def reload(ctx):
    if ctx.author.user.id == "338947895665360898":
        try:
            dh.update_data()
            await ctx.send(
                embeds=[Embed(
                    title="Successfully Updated sha-mapping",
                    description="\u200b",
                    colour=int("00ff00", 16)
                )], ephemeral=hidden
            )
        except BaseException as e:
            logger.warning(e)
            await ctx.send(
                embeds=[Embed(
                    title="Updating Local cache failed",
                    description="\u200b",
                    colour=int("ff0000", 16)
                )], ephemeral=hidden
            )


bot.start()
