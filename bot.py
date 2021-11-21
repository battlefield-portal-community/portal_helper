import os
from discord import ext,Embed
from discord_slash import SlashCommand # Importing the newly installed library.
from thefuzz import fuzz, process
from github_api import DataHandler
from dotenv import load_dotenv
load_dotenv()

bot = ext.commands.Bot(command_prefix="!")
slash = SlashCommand(bot, sync_commands=True) # Declares slash commands through the client.
dh = DataHandler()
dh.load_data()

guild_ids = [829265067073339403]


def special_embeds(block_name):
    pass


def make_embed(block_name):
    block_name = str(block_name).lower()
    if block_name == "all":
        # todo: Show Complete list of all blocks
        return special_embeds("all")
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
    title = doc_list[0]
    if "Inputs" in doc_list:
        content = doc_list[1:doc_list.index("Inputs")][0]
    else:
        content = doc_list[1:][0]
    if "Output" in doc_list:
        inputs = doc_list[doc_list.index("Inputs")+1:doc_list.index("Output")]
        output = doc_list[doc_list.index("Output") + 1:]
    else:
        inputs = doc_list[doc_list.index("Inputs") + 1:]

    inputs = " ".join(inputs)
    output = " ".join(output)

    notes = ''
    if "Notes" in inputs:
        tmp = inputs.split("Notes")
        notes = tmp[1]
        inputs = tmp[0]
        print(tmp,notes,inputs)
    if "Notes" in output:
        tmp = output.split("Notes")
        notes = tmp[1]
        output = tmp[0]
        print(tmp,notes,output)


    content_final = ""
    for word in content.split(" "):
        if word.isupper():
            content_final += f"**{word}** "
        else:
            content_final += f"{word} "

    embed = Embed(
        title=title,
        url=f"https://docs.bfportal.gg/docs/blocks/{title}",
        description=content_final
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
async def _d(ctx, block_name): # Defines a new "context" (ctx) command called "ping."
    try:
        embed = make_embed(block_name)
        await ctx.send(embed=embed)
    except ValueError as e:
        print(e)
        await ctx.send("Error getting doc")

bot.run(os.getenv("DISCORD_TOKEN"))
