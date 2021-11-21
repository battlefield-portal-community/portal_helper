import os
from discord import ext,Embed
from discord_slash import SlashCommand # Importing the newly installed library.
from thefuzz import fuzz, process
from github_api import DataHandler
from dotenv import load_dotenv
import logging
load_dotenv()
log_file = "log"

logging.basicConfig(filename=log_file,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
logging.info("New Start up!!")
bot = ext.commands.Bot(command_prefix="!")
slash = SlashCommand(bot, sync_commands=True) # Declares slash commands through the client.
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
        for i in range(4, len(doc_list)-1, 2):
            embed.add_field(
                name=doc_list[i],
                value=doc_list[i+1],
                inline=False
            )
        return embed

    if block_name == "all":
        embed = Embed(title="All Blocks",url="https://docs.bfportal.gg/docs/blocks")
        for block,value in dh.docs_dict.items():
            embed.add_field(name="\u200b", value=f"[{value[1]}](https://docs.bfportal.gg/docs/blocks/{value[1]})")
        return embed


def make_embed(block_name):
    block_name = str(block_name).lower()
    if block_name == "all":
        # todo: Show Complete list of all blocks
        return
#        return special_embeds("all")
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
        inputs = doc_list[doc_list.index("Inputs")+1:doc_list.index("Output")]
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



    embed = Embed(
        title=title,
        url=f"https://docs.bfportal.gg/docs/blocks/{title}",
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
    return embed


def get_closest_match(block):
    ratio_list = [(i, fuzz.ratio(block, i)) for i in dh.docs_dict.keys()]
    ratio_list.sort(key=lambda x: x[1], reverse=True)
    return ratio_list[0][0]


@bot.event
async def on_ready():
    print("Ready!")


@slash.slash(name="d", guild_ids=guild_ids, description="Returns Documentation of a block, type all to get all blocks")
async def _d(ctx, block_name):
    try:
        if block_name != "all":
            embed = make_embed(block_name)
            await ctx.send(embed=embed, delete_after=60*5)
        else:
            await ctx.send("Not yet Implemented", delete_after=60 * 5)
    except ValueError as e:
        logging.critical(e)
        await ctx.send("```\nError getting doc```", delete_after=10)

bot.run(os.getenv("DISCORD_TOKEN"))
