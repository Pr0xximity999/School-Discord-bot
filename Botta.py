#Import libraries
import discord
from discord import app_commands
import pandas as pd
import pathlib
import re
import time
voteType = ""
currUser = ""
voteStarted = False
hostUser = ""
userIndex = 0
itemCount = 0
voteCount = 0
votedGames = []
userDone = True
users = {}
addedItems = []
itemStage = {
    "addusers" : True,
    "additems" : False,
    "voteitems": False,
    "finalResults": False,
}


#Resets all the game values
def reset_values():
    global hostUser, voteStarted, users, addedItems, currUser, userIndex, itemCount, userDone, itemStage, voteCount, voteType, votedGames
    voteType = ""
    currUser = ""
    voteStarted = False
    hostUser = ""
    userIndex = 0
    itemCount = 0
    voteCount = 0
    userDone = True
    users = {}
    addedItems = []
    itemStage = {
        "addusers" : True,
        "additems" : False,
        "voteitems": False
    }

class MyClient(discord.Client):
    #When the bot has started
    async def on_ready(self):
        await tree.sync(guild=discord.Object(id=1145786156185829407))
        print(f'Logged on as {self.user}')

    #when there is a message sent
    async def on_message(self, message:discord.Message):
        global currUser, userDone, userIndex, itemCount, hostUser, voteType
        if(message.author == self.user): return #If the bot has sent the message, ignore it
        channel = client.get_channel(message.channel.id) #Sets the channel for replying

        #If the game stage is to add the users
        if(itemStage["addusers"]):
            if(message.author.id != hostUser): return #If the user is anything other than the host

            #If theres no mention in the message
            if(not "@" in message.content):         
                await channel.send("There's not a single user in that sentence")
                await channel.send("dumbass")

            #Go trough the message to add all the(unique users) users
            for _, user in enumerate(re.finditer(r"<.{19}>", message.content)):
                if user.group() not in users.keys():
                    if(not user.group()): continue 
                    users[user.group()] = {"vote1": "",
                                                "vote2": "",
                                                "vote3": ""}
            if(users == {}): return #If no users where found, ingore

            #Display the participating users and explains the rules
            await channel.send("Players who participate:")
            for user in users.keys():
                await channel.send(user)
            embed=discord.Embed(title=f"{voteType.upper()} STAGE", 
                                description=f"""Now all players will add their {voteType}s. \n
                                The {voteType} have to be unique, so no doubles \n
                                If you post doubles, they will be ignored \n
                                If you post more than 3 {voteType}s, the excess will be ignored \n
                                Seperate your choises with a comma (,)""", color=0x6de8af)
            embed.set_author(name="MetMatBot")
            embed.set_footer(text="If u read this then Matthew is gay")
            await channel.send(embed=embed)
            #Switch gamestage
            itemStage["addusers"] = False
            itemStage["additems"] = True
            
        #If the game stage is to add the games
        if(itemStage["additems"]):
            async def addGames():
                global currUser, userDone, userIndex, itemCount, hostUser
                if(userDone):
                    itemCount = 0
                    currUser = list(users.keys())[userIndex]
                    await channel.send(f"{currUser}, please add your 3 {voteType}s")
                    userDone = False
                    return

                if(message.author.id != int(currUser[2:-1])): return
                choises = message.content.split(",")
                choises = [i.strip().upper() for i in choises]
                for choise in choises:
                    if choise.upper() in addedItems: continue
                    if itemCount == 3: break
                    addedItems.append(choise.upper())
                    itemCount += 1

                if(itemCount < 2):
                    await channel.send(f"You still need to add {3 - itemCount} {voteType}(s)")
                    return
                
                userIndex += 1
                userDone = True
                if(userIndex + 1 > len(list(users.keys()))):
                    currUser = ""
                    itemStage["additems"] = False
                    itemStage["voteitems"] = True
                    userIndex = 0
                    embed=discord.Embed(title="VOTING STAGE", 
                        description=f"""Now all players will vote on the {voteType}s \n
                        Everyone will get 3 votes \n
                        The first vote is worth 3 points. \n
                        The second is worth 2 \n
                        The third and final vote is worth 1 \n
                        Invalid votes will be ignored\n
                        Seperate your choises with a comma (,)\n \n
                        **Added {voteType}s to vote on:**\n
                        {", ".join(addedItems)}""", color=0xff0000)
                    embed.set_author(name="MetMatBot")
                    await channel.send(embed=embed)
                else: await addGames()
            await addGames()

        #If the game stage is to vote the games
        if(itemStage["voteitems"]):
            async def voteGames():
                global currUser, userDone, userIndex, itemCount, hostUser, voteCount, votedGames
                if(userDone):
                    votedGames = []
                    voteCount = 0
                    currUser = list(users.keys())[userIndex]
                    userDone = False
                    await channel.send(f"{currUser}, please vote on your 3 {voteType}s")
                    return
                if(message.author.id != int(currUser[2:-1])): return

                choises = message.content.split(",")
                choises = [i.strip().upper() for i in choises]
                for choise in choises:
                    if not choise in addedItems: continue
                    if choise in votedGames: continue
                    if voteCount == 3: break
                    users[currUser][f"vote{voteCount + 1}"] = choise
                    votedGames.append(choise)
                    voteCount += 1

                if(voteCount < 3):
                    await channel.send(f"{3 - voteCount} {voteType}(s) werent valid and need to be re-entered")
                    return
                
                userIndex += 1
                userDone = True
                if(userIndex + 1 > len(list(users.keys()))):
                    currUser = ""
                    itemStage["voteitems"] = False
                    itemStage["finalResults"] = True
                    userIndex = 0
                else: await voteGames()
            await voteGames()

        if(itemStage["finalResults"]):
            voteResults = {}
            for item in addedItems:
                voteResults[item] = 0
            for user in users.values():
                    voteResults[user["vote1"]] += 3
                    voteResults[user["vote2"]] += 2
                    voteResults[user["vote3"]] += 1

            await channel.send(voteResults)
            hostUser = message.author.id
            reset_values()
            

#Gets the intents and adds them to the client
intents = discord.Intents.default()
intents.message_content = True

#Defines the client
client = MyClient(intents=intents)
#Sets the app commands
tree = app_commands.CommandTree(client)

#Sets the slash commands
@tree.command(name="start_vote", description="Starts the vote", guild=discord.Object(id=1145786156185829407))
async def start_vote(message, votetype:str="game"):
    global hostUser, voteStarted, voteType
    voteType = votetype
    if(voteStarted):
        await message.response.send_message(content=f"Voting has already started by <@{hostUser}>", ephemeral=True)
        return 
    voteStarted = True
    hostUser = message.user.id
    await message.response.send_message(f"Vote Started \n<@{hostUser}>, list all users that participate")

@tree.command(name="stop_vote", description="Starts the vote", guild=discord.Object(id=1145786156185829407))
async def stop_vote(message):
    if(not voteStarted):
        await message.response.send_message(content=f"No vote has been started yet", ephemeral=True)
        return 
    if(message.user.id != hostUser):
        await message.response.send_message(content=f"The vote can only be stopped by <@{hostUser}>", ephemeral=True)
        return
    reset_values()
    await message.response.send_message(f"Voting has been stopped")


#retrieves the api key from the csv and runs the client
secrets = pd.read_csv(f'{pathlib.Path(__file__).parent.resolve()}\secrets.csv')
apikey = secrets["APIKey"].values[0]
client.run(apikey)