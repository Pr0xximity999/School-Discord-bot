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
voteCount = 0
userDone = True
users = {}
addedGames = []
gameStage = {
    "addusers" : True,
    "addgames" : False,
    "votegames": False,
    "finalResults": False,
}


#Resets all the game values
def reset_values():
    global hostUser, voteStarted, users, addedGames, currUser, userIndex, gameCount, userDone, gameStage, gameFile, movieFile, voteCount
    movieFile = open("movieFile.txt", "a")
    gameFile = open("gameFile.txt", "a")
    currUser = ""
    voteStarted = False
    hostUser = ""
    userIndex = 0
    gameCount = 0
    voteCount = 0
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
        await tree.sync(guild=discord.Object(id=1145786156185829407))
        print(f'Logged on as {self.user}')

    #when there is a message sent
    async def on_message(self, message:discord.Message):
        global currUser, userDone, userIndex, gameCount, hostUser
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
            embed=discord.Embed(title="GAME STAGE", 
                                description="""Now all players will add their games. \n
                                The games have to be unique, so no doubles \n
                                If you post doubles, they will be ignored \n
                                If you post more than 3 games, the excess will be ignored \n
                                Seperate your choises with a comma (,)""", color=0x6de8af)
            embed.set_author(name="MetMatBot")
            embed.set_footer(text="If u read this then Matthew is gay")
            await channel.send(embed=embed)
            #Switch gamestage
            gameStage["addusers"] = False
            gameStage["addgames"] = True
            
        #If the game stage is to add the games
        if(gameStage["addgames"]):
            async def addGames():
                global currUser, userDone, userIndex, gameCount, hostUser
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
                    gameCount += 1

                if(gameCount < 2):
                    await channel.send(f"You still need to add {3 - gameCount} game(s)")
                    return
                
                userIndex += 1
                userDone = True
                if(userIndex + 1 > len(list(users.keys()))):
                    currUser = ""
                    gameStage["addgames"] = False
                    gameStage["votegames"] = True
                    userIndex = 0
                    embed=discord.Embed(title="VOTING STAGE", 
                        description="""Now all players will vote on the games \n
                        Everyone will get 3 votes \n
                        The first vote is worth 3 points. \n
                        The second is worth 2 \n
                        The third and final vote is worth 1 \n
                        Invalid votes will be ignored\n
                        Seperate your choises with a comma (,)""", color=0xff0000)
                    embed.set_author(name="MetMatBot")
                    await channel.send(embed=embed)
                    await channel.send(addedGames)
                else: await addGames()
            await addGames()

        #If the game stage is to vote the games
        if(gameStage["votegames"]):
            async def voteGames():
                global currUser, userDone, userIndex, gameCount, hostUser, voteCount
                if(userDone):
                    voteCount = 0
                    currUser = list(users.keys())[userIndex]
                    userDone = False
                    await channel.send(f"{currUser}, please vote on your 3 games")
                if(message.author.id != int(currUser[2:-1])): return

                choises = message.content.split(",")
                choises = [i.strip().upper() for i in choises]
                for choise in choises:
                    if not choise in addedGames: continue
                    if voteCount == 3: break
                    users[currUser][f"game{voteCount + 1}"] = choise
                    voteCount += 1

                if(voteCount < 3):
                    await channel.send(f"{3 - voteCount} werent valid and need to be re-entered")
                    return
                
                userIndex += 1
                userDone = True
                if(userIndex + 1 > len(list(users.keys()))):
                    currUser = ""
                    gameStage["votegames"] = False
                    gameStage["finalResults"] = True
                    userIndex = 0
                else: await voteGames()
            await voteGames()

        if(gameStage["finalResults"]):
            await channel.send(users)
            hostUser = message.author.id
            await stop_vote(message)
            

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