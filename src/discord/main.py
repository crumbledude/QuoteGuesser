import discord
from discord.ext import commands

import os
import sys
import asyncio
from dotenv import find_dotenv, load_dotenv
from colorama import  Fore

#Load environment variables
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

BOT_TOKEN = os.getenv("BOT_TOKEN")

#Set up the command prefix
client = commands.Bot(command_prefix="=", intents=discord.Intents.all())

#Runs when the bot connects to discord
@client.event
async def on_ready():
    print(f"{Fore.MAGENTA}Bot is connected to discord{Fore.RESET}")

#Used to sync the slash commands
@client.command(name="sync")
async def sync(ctx):
    synced = await client.tree.sync()
    print(f"Synced {len(synced)} command(s).")

@client.tree.command(name="ping", description="Shows the bot's latency in ms.")
async def ping(interaction: discord.Interaction):
    bot_latency = round(client.latency * 1000)
    await interaction.response.send_message(f"Bot latency: {bot_latency}ms", ephemeral=True)

#Used to load all of the files in the cog folder
async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")
            print(f"{Fore.YELLOW}{filename[:-3]} is loaded{Fore.RESET}")

async def main():
    async with client:
        #Load any cogs
        await load()
        #Run the bot
        await client.start(BOT_TOKEN)

#Runs the discord bot
asyncio.run(main())
