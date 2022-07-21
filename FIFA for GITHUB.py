import discord, random, json
from discord.ext import commands
from difflib import SequenceMatcher

client = commands.Bot(command_prefix = '!', intents = discord.Intents.all())

@client.event
async def on_ready():
    print("Ready for action. GLHF!")
    
@client.command()
async def register(ctx):
    with open("rosters.json", 'r+') as f:
        playerlist = json.load(f)
        playerlist[ctx.author.mention] = []
    with open("rosters.json", 'w') as f:
        json.dump(playerlist, f)
    await ctx.send(f'{ctx.author.mention} has been registered')

@client.command()
async def deregister(ctx):
    with open("rosters.json", 'r') as f:
        playerlist = json.load(f)
        playerlist.pop(ctx.author.mention)
    with open("rosters.json", 'w') as f:
        json.dump(playerlist, f)
    await ctx.send(f'{ctx.author.mention} has been deregistered')

@client.command()
async def clear(ctx):
    with open("rosters.json", 'w') as f:
        json.dump(dict(), f)
    await ctx.send("All players have been deregistered")

                    
    
class Draft(commands.Cog):
    def __init__(self):
        self.current = None
        self.full = None
        self.waiting = False
        self.potentials = []
    
    @staticmethod
    def _checkrosters(s):
        with open("rosters.json", 'r') as f:
            rosters = json.load(f).values()
            for i in rosters:
                if s in i:
                    return True
        return False
    
    @staticmethod
    def potential_pick(entry):
        final = list()
        with open("22_playernames_long.txt", 'r') as f:
            f = [i.strip() for i in f.readlines()]
            sims = []
            for line,name in enumerate(open("22_playernames_short_new.txt", 'r')):
                name = name.strip()
                sims.append((name, line, SequenceMatcher(a=entry, b=name).find_longest_match().size))
            x = sorted(sims, key = lambda s: -s[2])[:5]
        for i in x:
            final.append(f[i[1]])
        return final

    def create_order(self):
        with open("rosters.json", 'r') as f:
            self.order = list(json.load(f).keys())
        random.shuffle(self.order)
    
    def create_full_order(self, rostersize):
        for i in [(self.order if i % 2 == 0 else self.order[::-1]) for i in range(rostersize)]:
            for j in i:
                yield j
                    
    @commands.command()
    async def start(self, ctx, rostersize = 11):
        self.create_order()
        await ctx.send(''.join([f'{i}\n' for i in self.order]) + 'is your pick order')
        self.full = self.create_full_order(rostersize)
        self.current = next(self.full)
        await ctx.send(f'{self.current} it is your pick')
        
    @commands.Cog.listener()
    async def on_message(self, message):
        channel = message.channel
        if message.author.mention == self.current:
            if self.waiting == False:
                self.potentials = Draft.potential_pick(message.system_content)
                await channel.send('Did you mean:\n' + ''.join([f'{i}: {self.potentials[i]}\n' for i in range(len(self.potentials))]) + '5: Search Again')
                self.waiting = True
            elif self.waiting == True:
                if message.system_content in '01234':
                    if not Draft._checkrosters(self.potentials[int(message.system_content)]):
                        with open("rosters.json", 'r') as f:
                            rosters = json.load(f)
                            rosters[message.author.mention].append(self.potentials[int(message.system_content)])
                        with open("rosters.json", 'w') as f:    
                            json.dump(rosters, f)
                        self.waiting = False
                        try:
                            await channel.send(f'{next(self.full)} it is your pick')
                        except StopIteration:
                            await channel.send("Congratulations! The draft is finished")     
                            with open('rosters.json', 'r+') as f:
                                for i,j in json.load(f).items():
                                    user = await client.fetch_user(int(i[2:-1]))
                                    await user.send(''.join([f'{i}\n' for i in j]))
                                json.dump(dict(), f)
                            
                    else:
                        await channel.send("Player already taken. Please try again")
                        self.waiting = False
                elif message.system_content == '5':
                    await channel.send("Awaiting new pick")
                    self.waiting = False
                else:
                    await channel.send("Please select a number between 0 and 5")
                
                    
                    
                    
client.add_cog(Draft())

client.run("INSERT BOT TOKEN HERE")
