#Import libraries
import discord
import pandas as pd
import pathlib

client = discord.client
class MyClient(discord.Client):

    #When the bot has started
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    #when there is a message sent
    async def on_message(self, message):
        if(message.author.id != self.user.id):
            print(f'Message from {message.author}: {message.content}')

        if(message.author.id != self.user.id and message.content[0] == "-"):
            channel = client.get_channel(message.channel.id)
            await channel.send(message.content[1:])
           

        

#Gets the intents and adds them to the client
intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)

#retrieves the api key from the csv and runs the client
secrets = pd.read_csv(f'{pathlib.Path(__file__).parent.resolve()}\secrets.csv')
apikey = secrets["APIKey"].values[0]
client.run(apikey)
