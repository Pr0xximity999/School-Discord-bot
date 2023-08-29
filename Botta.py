#Import libraries
import discord
from discord.ext import commands
from discord.components import Button, ButtonStyle
import pandas as pd
import pathlib

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='-', intents=intents)

users = {}
games = []
votes = {}

@bot.event
async def on_ready():
    print(f'Bot is ingelogd als {bot.user}')


@bot.command()
async def send_embed(ctx):
    embed = discord.Embed(title="Input Form", description="Enter something:")
    await ctx.send(
        embed=embed,
        components=[
            Button(style=ButtonStyle.blurple, label="Click me!", custom_id="input_button"),
        ],
    )

@bot.event
async def on_button_click(interaction):
    if interaction.custom_id == "input_button":
        await interaction.respond(
            type=7,  # Acknowledge the interaction
            content="Please enter something:",
            components=[
                Button(style=ButtonStyle.blurple, label="Submit", custom_id="confirm_button"),
            ],
        )

@bot.event
async def on_button_click(interaction):
    if interaction.custom_id == "confirm_button":
        user_input = interaction.message.content  # Get the content of the message
        await interaction.respond(content=f"You entered: {user_input}")



@bot.command()
async def start_vote(ctx, game_name):
    

    if game_name not in games: 
        games.append(game_name)
        votes[game_name] = 0
    else: 
        ctx.send('Dat nummer is al toegevoegt!')
        return
    await ctx.send(f'{game_name} is toegevoegd aan de lijst!')

@bot.command()
async def show_gamelist(ctx):
    await ctx.send(games)

@bot.command()
async def vote(ctx, game_name):
    if game_name in games:
        if ctx.author.id not in votes:
            votes[ctx.author.id] = game_name
            await ctx.send(f'Je hebt gestemd voor {game_name}!')
        else:
            await ctx.send('Je hebt al gestemd!')
    else:
        await ctx.send('Dit spel staat niet in de lijst!')

@bot.command()
async def calculate_winner(ctx):
    for vote in votes.values():
        if vote in games:
            games[vote] += 1

    winner = max(games, key=games.get)
    await ctx.send(f'Het winnende spel is {winner}!')

#retrieves the api key from the csv and runs the client
secrets = pd.read_csv(f'{pathlib.Path(__file__).parent.resolve()}\secrets.csv')
apikey = secrets["APIKey"].values[0]
bot.run(apikey)
