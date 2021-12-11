import os
from discord import ext, Embed, Color
from discord.ext import tasks
from discord_slash import SlashCommand
from thefuzz import fuzz,  process
from github_api import DataHandler
from dotenv import load_dotenv
import logging

load_dotenv()
log_file = "log"
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("discord_slash").setLevel(logging.WARNING)
logging.basicConfig(filename=log_file,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
# logging.basicConfig(
#                     format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
#                     datefmt='%H:%M:%S',
#                     level=logging.DEBUG)
logging.info("New Start up!!")
bot = ext.commands.Bot(command_prefix="!")
slash = SlashCommand(bot, sync_commands=True)  # Declares slash commands through the client.
dh = DataHandler()
dh.load_data()

guild_ids = [829265067073339403, 870246147455877181, 451430013615734784]


def make_bold(text):
    content_final = ""
    for word in text.split(" "):
        if word.isupper():
            content_final += f"**{word}** "
        else:
            content_final += f"{word} "
    return content_final


def special_embeds(block_name):
    if block_name == "rule":
        doc_list = [i for i in dh.get_doc("rule").split("\n") if i != ""]
        embed = Embed(
            title=make_bold(doc_list[0]),
            url=f"https://docs.bfportal.gg/docs/blocks/{doc_list[0]}",
            description=doc_list[1] + f"\n**{doc_list[3]}**"
        )
        for i in range(4, len(doc_list) - 1, 2):
            embed.add_field(
                name=doc_list[i],
                value=doc_list[i + 1],
                inline=False
            )
        return embed

    if block_name == "all":
        embed = Embed(title="All Blocks", url="https://docs.bfportal.gg/docs/blocks")
        for block, value in dh.docs_dict.items():
            embed.add_field(name="\u200b", value=f"[{value[1]}](https://docs.bfportal.gg/docs/blocks/{value[1]})")
        return embed


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
    embed = Embed(
        title=title,
        url=f"https://docs.bfportal.gg/docs/blocks/{url}",
        description=content
    )
    if inputs:
        embed.add_field(
            name="Inputs",
            value=inputs,
            inline=False
        )
    if output:
        embed.add_field(
            name="Output",
            value=output
        )
    if notes:
        embed.add_field(
            name="Notes",
            value=notes,
            inline=False
        )
    #print(embed.url)
    return embed


def get_closest_match(block):
    ratio_list = [(i, fuzz.ratio(block, i)) for i in dh.docs_dict.keys()]
    ratio_list.sort(key=lambda x: x[1], reverse=True)
    return ratio_list[0][0]


@bot.event
async def on_ready():
    print("Ready!")
    purge_logs.start()


@tasks.loop(hours=24*7)  # after 7 days
async def purge_logs():
    with open("log", "w") as FILE:
        FILE.truncate(0)


@slash.slash(name="tools", description="A list of tools/resources made by community")
async def _tools(ctx):
    embed = Embed(
        title="By the Community For the Community",
        url="https://bfportal.gg/",
        description="**A list of tools/resources made by community**\u200B",
        color=Color.green(),
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

    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/908104736455155762/912999248910495784/Animation_logo_discord.gif")

    for i in fields:
        embed.add_field(**i)
        embed.add_field(**spacer)

    embed.set_footer(text="And lastly this bot which was made by [ gala#8316 ] \nMaintained at\n"
                          "https://github.com/p0lygun/portal-docs-bot")

    await ctx.send(embed=embed)


@slash.slash(name="d", description="Returns Documentation of a block")
async def _d(ctx, block_name):
    try:
        embed = make_embed(block_name)
        embed.set_footer(text="click on title to go to full documentation")
        await ctx.send(embed=embed)
    except NotImplementedError as e:
        logging.warning(e)
        await ctx.send(
            embed=Embed(
                title="Not Yet Implemented",
                description=f"Command {block_name}",
                colour=Color.red()
            ),
            delete_after=10
        )
    except BaseException as e:
        logging.warning(f"Error with {block_name} {get_closest_match(block_name)}")
    except ValueError as e:
        logging.critical(e)
        await ctx.send(
            embed=Embed(
                title=f"Error getting docs for {block_name}",
                description="\u200b",
                colour=Color.red()
            )
        )


@slash.slash(name="reload", description="reloads local cache on bot server")
async def reload(ctx):
    if ctx.author.guild_permissions.administrator:
        try:
            await ctx.send(
                embed=Embed(
                    title="Successfully Updated sha-mapping",
                    description="\u200b",
                    colour=Color.green()
                )
            )
        except BaseException as e:
            logging.warning(e)
            await ctx.send(
                embed=Embed(
                    title="Updating Local cache failed",
                    description="\u200b",
                    colour=Color.red()
                )
            )

bot.run(os.getenv("DISCORD_TOKEN"))
