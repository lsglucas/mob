import os
import asyncpg
import discord
import motor.motor_asyncio

from discord import Intents
from discord.ext import commands
from dotenv import dotenv_values

from utilities import main_messages_style, positive_emojis_list
from utilities_moodle import get_data_timer
from secret1 import DB_Username, DB_Password, Bot_token

config = dotenv_values(".env")


async def get_serverSettings(client, ctx) -> str:
    """Gets the server's prefix, the time in which getdata's will loop and the server's url, it's accessable at any cog"""

    try:
        data = client.pg_con.server.find_one({"_id": ctx.guild.id})

        client.prefix = data.get("prefix")

        client.url = data.get("moodle_url")

        try:
            get_data_timer[0] = data.get("loop_time")

        except TypeError or discord.errors:
            pass

        # print(prefix, client.timer)
        return client.prefix

    except AttributeError or TypeError:
        return "--"


intents = Intents.all()
client = commands.Bot(
    command_prefix=get_serverSettings, help_command=None, intents=intents
)

# Creates a connection with the Discord Database
async def create_db_pool():
    """Creates a connection with the database, it's accessible on any cog"""

    client.pg_con = motor.motor_asyncio.AsyncIOMotorClient(config["URI"])
    client.pg_con = client.pg_con["DiscordBot"]


# Load and get/initialize all the files .py(cogs) in the folder cogs
@client.command()
async def load(ctx, extension):
    """Load the chosen cog"""
    client.load_extension(f"cogs.{extension}")


@client.command()
async def unload(ctx, extension):
    """Unloads the chosen cog"""
    client.unload_extension(f"cogs.{extension}")


@client.command()
async def reload(ctx, extension=None):
    """Reload all extensions or only reload the chosen extension"""

    if not extension:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("_"):
                client.unload_extension(f"cogs.{filename[:-3]}")
                client.load_extension(f"cogs.{filename[:-3]}")

        await ctx.message.add_reaction(next(positive_emojis_list))

        embed = main_messages_style("All extensions were successfully reloaded")
        await ctx.send(embed=embed)
        print("All extensions were successfully reloaded")

    else:
        client.unload_extension(f"cogs.{extension}")
        client.load_extension(f"cogs.{extension}")

        await ctx.message.add_reaction(next(positive_emojis_list))

        embed = main_messages_style(
            f"{extension.capitalize()} was successfully reloaded"
        )
        await ctx.send(embed=embed)
        print(f"{extension.capitalize()} was successfully reloaded")


for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and not filename.startswith("_"):
        client.load_extension(f"cogs.{filename[:-3]}")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = main_messages_style(
            "Invalid command",
            f"Type {client.prefix}help to see the available commands",
        )
        await ctx.send(embed=embed)


@client.event
async def on_guild_join(guild):
    """Add the guild in the database"""

    doc = {
        "guildId": int(guild.id),
        "guildName": str(guild.name),
        "prefix": "--",
    }
    await client.pg_con.servers.insert_one(doc)


@client.event
async def on_guild_remove(guild):
    """Cleans the guild's data from the database"""

    await client.pg_con.execute(
        "DELETE FROM {bot_servers, bot_data, moodle_events, moodle_groups, moodle_professors, moodle_professors} WHERE guild_id = $1",
        int(guild.id),
    )

    await client.pg_con.execute(
        "DELETE FROM bot_roles WHERE guild_id = $1",
        str(guild.id),
    )


@client.event
async def on_member_join(member):
    """Gives the guild's default role if it exists"""

    try:
        role = await client.pg_con.servers.find_one(
            {"guildId": member.guild}, {"on_join_role": True}
        )

        await member.add_roles(role)

    except AttributeError or TypeError:
        return


client.loop.run_until_complete(create_db_pool())

client.run(Bot_token)
