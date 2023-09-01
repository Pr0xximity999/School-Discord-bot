#Import libraries
import discord
from discord import app_commands
import pandas as pd
import pathlib
import re
import time

movieFile = open("movieFile.txt", "a")
gameFile = open("gameFile.txt", "a")
currUser = ""
voteStarted = False
hostUser = ""
userIndex = 0
gameCount = 0
userDone = True
users = {}
addedGames = []
gameStage = {
    "addusers" : True,
    "addgames" : False,
    "votegames": False
}


#Resets all the game values
def reset_values():
    global hostUser, voteStarted, users, addedGames, currUser, userIndex, gameCount, userDone, gameStage, gameFile, movieFile
    movieFile = open("movieFile.txt", "a")
    gameFile = open("gameFile.txt", "a")
    currUser = ""
    voteStarted = False
    hostUser = ""
    userIndex = 0
    gameCount = 0
    userDone = True
    users = {}
    addedGames = []
    gameStage = {
        "addusers" : True,
        "addgames" : False,
        "votegames": False
    }

class MyClient(discord.Client):
    #When the bot has started
    async def on_ready(self):
        reset_values()
        await tree.sync(guild=discord.Object(id=1145786156185829407))
        print(f'Logged on as {self.user}')

    #when there is a message sent
    async def on_message(self, message:discord.Message):
        global currUser, userDone, userIndex, gameCount
        if(message.author == self.user): return #If the bot has sent the message, ignore it
        channel = client.get_channel(message.channel.id) #Sets the channel for replying

        #If the game stage is to add the users
        if(gameStage["addusers"]):
            if(message.author.id != hostUser): return #If the user is anything other than the host

            #If theres no mention in the message
            if(not "@" in message.content):         
                await channel.send("There's not a single user in that sentence")
                await channel.send("dumbass")

            #Go trough the message to add all the(unique users) users
            for _, user in enumerate(re.finditer(r"<.{19}>", message.content)):
                if user.group() not in users.keys():
                    if(not user.group()): continue 
                    users[user.group()] = {"game1": "",
                                                "game2": "",
                                                "game3": ""}
            if(users == {}): return #If no users where found, ingore

            #Display the participating users and explains the rules
            await channel.send("Players who participate:")
            for user in users.keys():
                await channel.send(user)
            await channel.send("---------------------------")
            await channel.send("GAME STAGE")
            time.sleep(1)
            await channel.send("Now all players will add their games\n ")
            time.sleep(1)
            await channel.send("The games have to be unique, so no doubles")
            time.sleep(1)
            await channel.send("If you post doubles, they will be ignored")
            time.sleep(1)
            await channel.send("If you post more than 3 games, the excess will be ignored")
            time.sleep(1)
            await channel.send("Seperate your choises with a comma (,)\n---------------------------")
            #Switch gamestage
            gameStage["addusers"] = False
            gameStage["addgames"] = True
            
        #If the game stage is to add the games
        if(gameStage["addgames"]):
            if(userDone):
                gameCount = 0
                currUser = list(users.keys())[userIndex]
                await channel.send(f"{currUser}, please add your 3 games")
                userDone = False
                return

            if(message.author.id != int(currUser[2:-1])): return
            choises = message.content.split(",")
            choises = [i.strip().upper() for i in choises]
            for choise in choises:
                if choise in addedGames: continue
                if gameCount == 3: break
                addedGames.append(choise)
                gameFile.write(choise+"\n")
                gameCount += 1

            print(addedGames)
            if(gameCount < 3):
                await channel.send(f"You still need to add {3 - gameCount} game(s)")
                return
            
            userIndex += 1
            if(userIndex + 1 > len(list(users.keys()))):
                gameStage["addgames"] = False
                gameStage["votegames"] = True
            userDone = True
            gameFile.close()

        #If the game stage is to vote the games
        if(gameStage["votegames"]):
            await channel.send("---------------------------")
            await channel.send("VOTING STAGE")
            time.sleep(1)
            await channel.send("Now all players will vote on the games\n ")
            time.sleep(1)
            await channel.send("Everyone will get 3 votes")
            time.sleep(1)
            await channel.send("The first vote is worth 3 points")
            time.sleep(1)
            await channel.send("The second is worth 2 ")
            time.sleep(1)
            await channel.send("The third and final vote is worth 3 ")
            time.sleep(1)
            await channel.send("Seperate your choises with a comma (,)\n---------------------------")
            await channel.send(addedGames)
                

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

    if(message.user.id != hostUser):
        await message.response.send_message(content=f"The vote can only be stopped by <@{hostUser}>", ephemeral=True)
        return
    if(not voteStarted):
        await message.response.send_message(content=f"No vote has been started yet", ephemeral=True)
        return 
    reset_values()
    await message.response.send_message(f"Voting has been stopped")


#retrieves the api key from the csv and runs the client
secrets = pd.read_csv(f'{pathlib.Path(__file__).parent.resolve()}\secrets.csv')
apikey = secrets["APIKey"].values[0]
client.run(apikey)