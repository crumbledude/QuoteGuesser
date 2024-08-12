import discord
from discord.ext import commands
from discord import app_commands
from dotenv import find_dotenv, load_dotenv

import sys
import os

sys.path.insert(0, os.path.abspath("./cog_helpers"))
from guess import GuessGame
sys.path.insert(1, os.path.abspath("../common"))
from db_connector import Db

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
        self.game = None
        #try to connect to the database
        self.actuall_db = Db(TEST_DB_IP, "25576", TEST_DB_USER, TEST_DB_PASS, "test")
    
    #Runs after connected to discord
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"DBCommands.py is ready")
        

    #Runs after each message sent and checks if it is to do with the game
    @commands.Cog.listener()
    async def on_message(self, message):
        #Check if a quote game is running
        if self.game is not None: #check if created
            #it is
            if self.game.active:
                #run
                await self.on_message_logic(message)
            else:
                #dont run
                pass

    #The logic for the message checking
    async def on_message_logic(self, message):
        #If a game is running, check the message is in the right channel and it is not the bots message
        if message.channel.id == self.game.channel.id and message.author.id != self.client.user.id:
            #If someone guesses who said the quote, this is  run

            #EDGE CASE - for if someone has quoted themselves
            if self.game.who_quoted == self.game.who_said and message.content.lower().strip() == self.game.who_quoted:
                self.game.round_said_guessed = message.author.id
                self.game.round_quote_guessed = message.author.id
                await self.game.successful_guess(True)
                await self.game.successful_guess(False)

            if message.content.lower().strip() in self.game.who_said:
                if self.game.round_said_guessed is None:
                    #If someone has guessed who has said the quote
                    self.game.round_said_guessed = message.author.id
                    await self.game.successful_guess(True)
                else:
                    #If someone guesses the who said after someone else has
                    await message.channel.send("Who said already guessed")
            #If someone gusses who quoted, this is run
            elif message.content.lower().strip() in self.game.who_quoted:
                if self.game.round_quote_guessed is None:
                    #If someone has guessed who has quoted the quote
                    self.game.round_quote_guessed = message.author.id
                    await self.game.successful_guess(False)
                else:
                    #If someone guesses the who quoted after someone else has
                    await message.channel.send("Who quoted already guessed")

            #Need to add people who guessed to a scoreboard
            if self.game.round_quote_guessed is not None and self.game.round_said_guessed is not None:
                #Both thing have been guessed, run score and cancel task
                await self.game.score()
        #Check how many rounds are left

    @app_commands.command(name="start_game", description="Starts the quote guessing game")
    async def start_game(self, interaction: discord.Interaction):

        #Check if game is created, if it is, check if it is active, if it is, dont run, if not then run
        #If it is not created, then run

        if self.game is not None: #check if created
            #it is
            if not self.game.active:
                #run
                await self.start_game_logic(interaction)
            else:
                #dont run
                await interaction.response.send_message("There is already a game running!", ephemeral=True)
        else:
            #run
            await self.start_game_logic(interaction)

    async def start_game_logic(self, interaction):
        self.game = GuessGame(interaction.channel, interaction.user.id, self.actuall_db, self.client)
        self.game.active = True
        self.game.game_loop.start()
        await interaction.response.send_message("Game successfully created", ephemeral=True)


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



#Called when the file is loaded by main.py
async def setup(client):
    try:
        await client.add_cog(DbCommands(client))
    except:
        #If you cannot connect to the database, then stop this file from loading
        print(f"Cannot connect to database, so Db commands isn't ready")
    