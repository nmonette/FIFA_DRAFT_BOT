import discord
from discord.ext import commands
import random
import json

client = commands.Bot(command_prefix = '!',intents=discord.Intents.all())

@client.event
async def on_ready():
    print('Bot is ready.')

@client.command()
async def register(ctx):
    with open('PATH TO playerlist.json', 'r') as f:
        playerdict = json.load(f)
    playerdict[ctx.author.id] = ctx.author.mention
    with open('PATH TO playerlist.json', 'w') as f:
        json.dump(playerdict, f)
    await ctx.send(f'{ctx.author.mention} has been registered')

@client.command()
async def deregister(ctx):
    with open(''PATH TO playerlist.json'', 'r') as f:
        playerdict = json.load(f)
    playerdict.pop(f'{ctx.author.id}')
    with open(''PATH TO playerlist.json', 'w') as f:
        json.dump(playerdict, f)
    await ctx.send(f'{ctx.author.mention} has been deregistered')    

class Draft(commands.Cog):
    def __init__(self, playerlist):
        self.playertaken = False
        self.draftstart = False
        self.currentpick = ''
        self.playerlist = []
        self.pickorder = []
        self.rostersize = 0
        self.pickcount = 0




    @commands.command()
    async def clear(self, ctx):
        with open('PATH TO playerlist.json', 'r') as f:
            playerdict = json.load(f)
        playerdict = dict()
        with open('PATH TO playerlist.json', 'w') as f:
            json.dump(playerdict, f)
        await ctx.send('All players have been deregistered')

    def checkrosters(self, string):
        for name in self.playerlist:
            with open(f'{name}_roster', 'r') as f:
                checker = json.load(f)
            for key in checker:
                if string.lower() in checker[key].lower() or checker[key].lower() in string.lower():
                    return True
            return False

    @commands.command()
    async def start(self, ctx, rostersize=11):
        with open('PATH TO playerlist.json', 'r') as f:
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
        channel = message.channel
        if self.draftstart == True:
            if message.author.mention == self.currentpick:
                if self.checkrosters(message.content) == False:
                    with open(f'{message.author.mention}_roster', 'r') as f:
                        newchange = json.load(f)
                    with open(f'{message.author.mention}_roster', 'w') as f:
                        newchange[self.pickcount] = message.content
                        json.dump(newchange, f)
                    self.pickcount += 1
                else:
                    await channel.send("Player already taken, please try again")
                if self.pickcount == len(self.pickorder):
                    await channel.send("Congratulations! The draft has concluded")
                    self.__init__(self.playerlist)
                    with open('PATH TO playerlist.json', 'r') as f:
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


client.run("BOT TOKEN OMITTED")
