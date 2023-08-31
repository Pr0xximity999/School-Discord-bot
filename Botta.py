#Import libraries
import discord
from discord import app_commands
import pandas as pd
import pathlib
import re

voteStarted = False
hostUser = ""
users = {}

class MyClient(discord.Client):
    #When the bot has started
    async def on_ready(self):
        await tree.sync(guild=discord.Object(id=1145786156185829407))
        print(f'Logged on as {self.user}')

    #when there is a message sent
    async def on_message(self, message):
        if(message.author == self.user): return
        if(message.author.id == hostUser):
            channel = client.get_channel(message.channel.id)
            if(not "@" in message.content):
                
                await channel.send("There's not a single user in that sentence")
                await channel.send("dumbass")
            for _, user in enumerate(re.finditer(r"<.{19}>", message.content)):
                if user.group() not in users.keys():
                    if(not user.group()): continue 
                    users[user.group()] = {"game1": "",
                                                 "game2": "",
                                                 "game3": ""}
            if(users == {}): return
            await channel.send("Players who participate:")
            for user in users.keys():
                await channel.send(user)


#Gets the intents and adds them to the client
intents = discord.Intents.default()
intents.message_content = True

#Defines the client
client = MyClient(intents=intents)
#Sets the app commands
tree = app_commands.CommandTree(client)

#Sets the slash commands
@tree.command(name="start_vote", description="Starts the vote", guild=discord.Object(id=1145786156185829407))
async def start_vote(message):
    global hostUser, voteStarted
    if(voteStarted):
        await message.response.send_message(content=f"Voting has already started by <@{hostUser}>", ephemeral=True)
        return 
    voteStarted = True
    hostUser = message.user.id
    await message.response.send_message(f"Vote Started \n<@{hostUser}>, list all users that participate")

@tree.command(name="stop_vote", description="Starts the vote", guild=discord.Object(id=1145786156185829407))
async def stop_vote(message):
    global hostUser, voteStarted, users
    if(message.user.id != hostUser):
        await message.response.send_message(content=f"The vote can only be stopped by <@{hostUser}>", ephemeral=True)
        return
    if(not voteStarted):
        await message.response.send_message(content=f"No vote has been started yet", ephemeral=True)
        return 
    users = {}
    hostUser = ""
    voteStarted = False
    await message.response.send_message(f"Voting has been stopped")


#retrieves the api key from the csv and runs the client
secrets = pd.read_csv(f'{pathlib.Path(__file__).parent.resolve()}\secrets.csv')
apikey = secrets["APIKey"].values[0]
client.run(apikey)