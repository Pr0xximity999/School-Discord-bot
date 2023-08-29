#Import libraries
import discord
from discord import app_commands
import pandas as pd
import pathlib

class MyClient(discord.Client):
    
    #When the bot has started
    async def on_ready(self):
        await tree.sync(guild=discord.Object(id=1145786156185829407))
        print(f'Logged on as {self.user}!')

    #when there is a message sent
    async def on_message(self, message):
        if(message.author == self.user): return
        
        print(f'Message from {message.author}: {message.content}')

        if(message.content[0] == "-"):
            try:
                channel = client.get_channel(message.channel.id)
                msg = await channel.fetch_message(message.id)
                await msg.delete()
                await channel.send(message.content[1:])
            except:
                pass

#Gets the intents and adds them to the client
intents = discord.Intents.default()
intents.message_content = True

#Defines the client
client = MyClient(intents=intents)
#Sets the app commands
tree = app_commands.CommandTree(client)

#Sets the slash commands
@tree.command(name="testcommand",  description="this does something", guild=discord.Object(id=1145786156185829407))
async def embed_command(interaction, parameter1: int = 10):
    await interaction.response.send_message("Piss")

#retrieves the api key from the csv and runs the client
secrets = pd.read_csv(f'{pathlib.Path(__file__).parent.resolve()}\secrets.csv')
apikey = secrets["APIKey"].values[0]
client.run(apikey)
