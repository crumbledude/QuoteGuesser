import discord
from discord.ext import commands
from discord import app_commands
from common.db_connector import Db
import os
from dotenv import find_dotenv, load_dotenv
from colorama import Fore

#Find envrionment variables
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

#Get enviroment variables
TEST_DB_IP = os.getenv("TEST_DB_IP")
TEST_DB_USER = os.getenv("TEST_DB_USER")
TEST_DB_PASS = os.getenv("TEST_DB_PASS")

class DbCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        #try to connect to the database
        self.actuall_db = Db(TEST_DB_IP, "25576", TEST_DB_USER, TEST_DB_PASS, "test")
    
    #Runs after connected to discord
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{Fore.GREEN}DBCommands.py is ready{Fore.RESET}")
        
    #Send a random quote
    @app_commands.command(name="random_quote", description="Sends a random quote")
    async def rand_quote(self, interaction: discord.Interaction):
        print("test")
        quote_embed = discord.Embed(title="Random quote", colour=discord.Colour.random())
        dbdata = self.actuall_db.get_rand_value("quotetbl")
        quote_embed.add_field(name="Quote:", value=f"{dbdata[2]}")
        quote_embed.add_field(name="Said by:", value=f"{dbdata[0]}")
        quote_embed.add_field(name="When: ", value=f"{dbdata[5]}")
        quote_embed.add_field(name="NSFW: ", value=f"{dbdata[4]}")
        quote_embed.add_field(name="Where", value=f"{dbdata[6]}")
        quote_embed.set_footer(text=f"Quoted by {dbdata[1]}")
        
        await interaction.response.send_message(embed = quote_embed)
        
    
        

#Called when the file is loaded by main.py
async def setup(client):
    try:
        await client.add_cog(DbCommands(client))
    except:
        #If you cannot connect to the database, then stop this file from loading
        print(f"{Fore.RED}Cannot connect to database, so Db commands isn't ready{Fore.RESET}")
    