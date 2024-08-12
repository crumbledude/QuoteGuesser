import discord
from discord.ext import tasks, commands

class GuessGame:
    def __init__(self, channel, user, database, client):
        self.channel = channel
        self.user = user
        self.game_db = database
        self.bot_client = client
        self.quote = ""
        self.who_said = []
        self.who_quoted = []
        self.active = False
        self.rounds = 5
        self.round_said_guessed = None
        self.round_quote_guessed = None
        self.scoreboard = {}
        self.is_starting = True

    #Need to get a random quote and then send it
    async def send_quote_message(self):
        #Get a random quote, who said it and any alias, then make a new game object
        rand_quote = self.game_db.get_rand_value("quotetbl")
        print(rand_quote)
        self.quote = rand_quote[2]
        sayer_name_table = self.game_db.get_name(rand_quote[0])
        quoter_name_table = self.game_db.get_name(rand_quote[1])

        sayer_aliases = [sayer_name_table[1].lower(), sayer_name_table[2].lower()]
        quoter_aliases = [quoter_name_table[1].lower(), quoter_name_table[2].lower()]

        #Used for if they have more than one or more aliases
        if sayer_name_table[3] is not None:
            if "," in sayer_name_table[3]:
                #more than one alias
                alaises = sayer_name_table[3].split(",")
                for alais in alaises:
                    sayer_aliases.append(alais.lower())
            else:
                sayer_aliases.append(sayer_name_table[3].lower())

        if quoter_name_table[3] is not None:
            if "," in quoter_name_table[3]:
                #more than one alias
                alaises = quoter_name_table[3].split(",")
                for alais in alaises:
                    quoter_aliases.append(alais.lower())
            else:
                quoter_aliases.append(quoter_name_table[3].lower())

        self.who_said = sayer_aliases
        self.who_quoted = quoter_aliases

        self.is_starting = False

        quote_embed = discord.Embed(title="Guess who quoted & said this quote", color=discord.Color.gold())
        quote_embed.add_field(name="Quote:", value=self.quote)
        await self.channel.send(embed = quote_embed)

    @tasks.loop(seconds=30, name="GameLoop")
    async def game_loop(self):
        if not self.is_starting:
            embed = discord.Embed(title="Not guessed in time", color=discord.Color.red())
            embed.add_field(name="Quote", value=self.quote)
            embed.add_field(name="Said by", value=f"{self.who_said[0].capitalize()} {self.who_said[1][:1].capitalize()}")
            embed.add_field(name="Quoted by", value=f"{self.who_quoted[0].capitalize()} {self.who_quoted[1][:1].capitalize()}")
            embed.set_footer(text=f"Better luck next time :(")
            await self.channel.send(embed = embed)
            await self.score()
        else:
            await self.send_quote_message()

    async def score(self):
        self.game_loop.cancel()
        #Scoring for who quoted the quote
        if self.round_quote_guessed is not None:
            if self.round_quote_guessed in self.scoreboard:
                self.scoreboard[self.round_quote_guessed] += 1
            else:
                self.scoreboard[self.round_quote_guessed] = 1

        #Scoring for who said the quote
        if self.round_said_guessed is not None:
            if self.round_said_guessed in self.scoreboard:
                self.scoreboard[self.round_said_guessed] += 1
            else:
                self.scoreboard[self.round_said_guessed] = 1

        print(self.scoreboard)

        self.rounds -= 1
        print(f"Rounds left: {self.rounds}")
        self.round_said_guessed = None
        self.round_quote_guessed = None

        if self.rounds > 0:
            self.is_starting = True
            self.game_loop.restart()
        elif self.rounds == 0:
            #Allow the game to be started again
            self.active = False
            # Print the scoreboard
            sorted_scoreboard = {k: v for k, v in sorted(self.scoreboard.items(), key=lambda item: item[1])}
            keys = list(reversed(sorted_scoreboard))
            embed = discord.Embed(title="Scoreboard", color=discord.Color.blurple())
            if len(sorted_scoreboard) == 0:
                embed.add_field(name="No one won", value=":(")
            if len(sorted_scoreboard) > 0:
                embed.add_field(name="First place:", value= f"{self.bot_client.get_user(keys[0]).name} with {sorted_scoreboard[keys[0]]} points")
            if len(sorted_scoreboard) > 1:
                embed.add_field(name="Second place:", value= f"{self.bot_client.get_user(keys[1]).name} with {sorted_scoreboard[keys[1]]} points")
            if len(sorted_scoreboard) > 2:
                embed.add_field(name="Third place:", value= f"{self.bot_client.get_user(keys[2]).name} with {sorted_scoreboard[keys[2]]} points")

            await self.channel.send(embed=embed)



    async def successful_guess(self, is_who_said):
        if is_who_said:
            person = self.bot_client.get_user(self.round_said_guessed)
            embed = discord.Embed(title="Who said guessed!", color=discord.Color.green())
            embed.add_field(name="Quote", value=self.quote)
            embed.add_field(name="Said by", value=f"{self.who_said[0].capitalize()} {self.who_said[1][:1].capitalize()}")
            embed.set_footer(text=f"Guessed by {person.name}")
            await self.channel.send(embed = embed)
        else:
            person = self.bot_client.get_user(self.round_quote_guessed)
            embed = discord.Embed(title="Who quoted guessed!", color=discord.Color.green())
            embed.add_field(name="Quote", value=self.quote)
            embed.add_field(name="Quoted by", value=f"{self.who_quoted[0].capitalize()} {self.who_quoted[1][:1].capitalize()}")
            embed.set_footer(text=f"Guessed by {person.name}")
            await self.channel.send(embed = embed)
