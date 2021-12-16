import discord
from discord.ext import commands
import random
import json
import csv

client = commands.Bot(command_prefix = '!',intents=discord.Intents.all())

@client.event
async def on_ready():
    """Let the user know the bot is ready."""
    print('Bot is ready.')

@client.command()
async def register(ctx):
    """Add users wanting to partcipate in the draft to a JSON file of player ID's."""
    with open('playerlist.json', 'r') as f:
        playerdict = json.load(f)
    playerdict[ctx.author.id] = ctx.author.mention
    with open('playerlist.json', 'w') as f:
        json.dump(playerdict, f)
    await ctx.send(f'{ctx.author.mention} has been registered')

@client.command()
async def deregister(ctx):
    """Removes users from the aforementioned registration file."""
    with open('playerlist.json', 'r') as f:
        playerdict = json.load(f)
    playerdict.pop(f'{ctx.author.id}')
    with open('playerlist.json', 'w') as f:
        json.dump(playerdict, f)
    await ctx.send(f'{ctx.author.mention} has been deregistered')

def potential_pick(entry):
        """Return a list of potential players to be picked based off of the 
        user's entry."""
        potentials = list()
        with open("22_playernames_short_new.txt") as short:
            short = short.readlines()
            with open("22_playernames_long.txt") as long:
                long = long.readlines()
                for i in range(len(short)):
                    if short[i] in entry or entry in short[i]:
                        potentials.append(long[i])
            return potentials

class Draft(commands.Cog):
    def __init__(self, playerlist):
        self.playertaken = False
        self.draftstart = False
        self.currentpick = ''
        self.playerlist = []
        self.pickorder = []
        self.rostersize = 0
        self.pickcount = 0
        self.checked = False
        self.waiting = False
        self.potentials = []

    @commands.command()
    async def clear(self, ctx):
        """Remove all players from the registration file."""
        with open('playerlist.json', 'r') as f:
            playerdict = json.load(f)
        playerdict = dict()
        with open('playerlist.json', 'w') as f:
            json.dump(playerdict, f)
        await ctx.send('All players have been deregistered')

    def checkrosters(self, string):
        """Checks to see if a player has been taken already or not"""
        for name in self.playerlist:
            with open(f'{name}_roster', 'r') as f:
                checker = json.load(f)
            for key in checker:
                if string.lower() in checker[key].lower() or checker[key].lower() in string.lower():
                    return True
            return False


    @commands.command()
    async def start(self, ctx, rostersize=11):
        """Begin the draft"""
        with open('playerlist.json', 'r') as f:
            playerdict = json.load(f)
        for key in playerdict:
            self.playerlist += [playerdict[key]]
        self.rostersize = int(rostersize)
        random.shuffle(self.playerlist)
        for name in self.playerlist:
            await ctx.send(name)
        await ctx.send('is your pick order')
        status = []
        for num in range(self.rostersize):
            if num % 2 == 0:
                status.append("Forward")
            else:
                status.append("Backward")
        for direction in status:
            reverse = self.playerlist[::-1]
            if direction == "Forward":
                for name in [self.playerlist]:
                    self.pickorder += name
            else:
                for name in [reverse]:
                    self.pickorder += name
        for name in self.playerlist:
            emptydict = dict()
            with open(f'{name}_roster', 'w') as f:
                json.dump(emptydict, f)
        self.draftstart = True
        self.currentpick = self.pickorder[self.pickcount]
        await ctx.send(f'{self.currentpick} it is your pick')




    @commands.Cog.listener()
    async def on_message(self, message):
        """Record the draft picks of each player."""
        channel = message.channel
        if self.draftstart == True:
            if message.author.mention == self.currentpick:
                if self.checked == False and self.waiting == False:
                    self.potentials = potential_pick(message.content)
                    if self.potentials is not None:
                        count = 1
                        sender = ""
                        for i in self.potentials:
                            sender += f"{count}: {i}"
                            count += 1
                        await channel.send(f"Do you mean:\n{sender}")
                        self.waiting = True
                    else:
                        await channel.send("No player(s) found. Please try again.")
                elif self.waiting == True:
                    try:
                        player = self.potentials[int(message.content) -1]
                        self.waiting = False
                        self.checked = True
                    except:
                        await channel.send("Please submit one of the given numbers.")
                try:
                    if self.checkrosters(player) == False:
                        with open(f'{message.author.mention}_roster', 'r') as f:
                            newchange = json.load(f)
                            self.checked = False
                        with open(f'{message.author.mention}_roster', 'w') as f:
                            newchange[self.pickcount] = player
                            json.dump(newchange, f)
                        self.pickcount += 1
                    else:
                        await channel.send("Player already taken, please try again")
                        self.checked = False
                except:
                    pass
                if self.pickcount == len(self.pickorder):
                    await channel.send("Congratulations! The draft has concluded")
                    self.__init__(self.playerlist)
                    with open('playerlist.json', 'r') as f:
                        playerroster = json.load(f)
                    for key in playerroster:
                        user = await client.fetch_user(int(key))
                        value = playerroster[key]
                        with open(f'{value}_roster', 'r') as f:
                            draftlist = json.load(f)
                        for key in draftlist:
                            value = draftlist[key]
                            await user.send(str(value))
                else:
                    self.currentpick = self.pickorder[self.pickcount]
                    await channel.send(f'{self.currentpick} it is your pick')



client.add_cog(Draft(client))

client.run("TOKEN REMOVED")

