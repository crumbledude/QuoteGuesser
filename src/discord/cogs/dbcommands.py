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

class GuessGame:
    def __init__(self, channel, user, quote, who_said, who_quoted, bot_client):
        self.channel = channel
        self.user = user
        self.quote = quote
        self.who_said = who_said
        self.who_quoted = who_quoted
        self.bot_client = bot_client
        self.active = True
        self.who_quoted_guessed = False
        self.who_said_guessed = False

    async def send_quote_message(self):
        quote_embed = discord.Embed(title="Guess who quoted & said this quote", color=discord.Color.gold())
        quote_embed.add_field(name="Quote:", value=self.quote)
        await self.channel.send(embed = quote_embed)



class DbCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.game = None
        #try to connect to the database
        self.actuall_db = Db(TEST_DB_IP, "25576", TEST_DB_USER, TEST_DB_PASS, "test")
    
    #Runs after connected to discord
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{Fore.GREEN}DBCommands.py is ready{Fore.RESET}")
        
    @commands.Cog.listener()
    async def on_message(self, message):
        #Check if a quote game is running
        if self.game.active:
            #If a game is running, check the message is in the right channel and it is not the bots message
            if message.channel.id == self.game.channel.id and message.author.id != self.client.user.id:
                #If someone guesses who said the quote, this is  run
                if message.content.lower().strip() in self.game.who_said:
                    if self.game.who_said_guessed == False:
                        await message.channel.send("Who said guessed")
                        self.game.who_said_guessed = True
                    else:
                        await message.channel.send("Who said already guessed")

    #Send a random quote
    @app_commands.command(name="random_quote", description="Sends a random quote")
    async def rand_quote(self, interaction: discord.Interaction):
        quote_embed = discord.Embed(title="Random quote", colour=discord.Colour.random())
        dbdata = self.actuall_db.get_rand_value("quotetbl")
        quote_embed.add_field(name="Quote:", value=f"{dbdata[2]}")

        #Get name of sayer
        result_sayer = self.actuall_db.get_name(dbdata[0])
        first_sayer = result_sayer[1]
        last_sayer = result_sayer[2]
        quote_embed.add_field(name="Said by:", value=f"{first_sayer} {last_sayer}")

        quote_embed.add_field(name="When: ", value=f"{dbdata[5]}")

        #Is it nsfw?
        if dbdata[4] == 1:
            nsfw = "Yes"
        else:
            nsfw = "No"
        quote_embed.add_field(name="NSFW: ", value=f"{nsfw}")

        result_location = self.actuall_db.get_location(dbdata[6])
        quote_embed.add_field(name="Where", value=f"{result_location[1]}")

        #Get name of quoter
        result_quoter = self.actuall_db.get_name(dbdata[1])
        first_quoter = result_quoter[1]
        last_quoter = result_quoter[2]
        quote_embed.set_footer(text=f"Quoted by {first_quoter} {last_quoter}")
        
        await interaction.response.send_message(embed = quote_embed)
        

    @app_commands.command(name="start_game", description="Starts the quote guessing game")
    async def start_game(self, interaction: discord.Interaction):
        #Get a random quote, who said it and any alias, then make a new game object
        rand_quote = self.actuall_db.get_rand_value("quotetbl")
        print(rand_quote)
        sayer_name_table = self.actuall_db.get_name(rand_quote[0])
        quoter_name_table = self.actuall_db.get_name(rand_quote[1])

        sayer_aliases = [sayer_name_table[1].lower(), sayer_name_table[2].lower()]
        quoter_aliases = [quoter_name_table[1].lower(), quoter_name_table[2].lower()]

        #Add any aliases ------- NEEED TO IMPLIMENT IF THEY HAVE MORE THAN ONE ALIAS
        # if sayer_name_table[3]:
        #     for name in sayer_name_table[3].lower():
        #         sayer_aliases.append(name)
        #
        # if quoter_name_table[3]:
        #     for name in quoter_name_table[3].lower():
        #         quoter_aliases.append(name)
        
        if sayer_name_table[3]:
            sayer_aliases.append(sayer_name_table[3].lower())

        if quoter_name_table[3]:
            quoter_aliases.append(quoter_name_table[3].lower())

        print(f"sayer aliases: {sayer_aliases}")
        self.game = GuessGame(interaction.channel, interaction.user.id, rand_quote[2], sayer_aliases, quoter_aliases, self.client)
        await self.game.send_quote_message()

        await interaction.response.send_message("Game successfully created", ephemeral=True)



#Called when the file is loaded by main.py
async def setup(client):
    try:
        await client.add_cog(DbCommands(client))
    except:
        #If you cannot connect to the database, then stop this file from loading
        print(f"{Fore.RED}Cannot connect to database, so Db commands isn't ready{Fore.RESET}")
    