import os
import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv
import psycopg2

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
DBNAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PW = os.getenv('DB_PW')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
APIKEY = os.getenv('APIKEY')


connection = psycopg2.connect(dbname=DBNAME, user=DB_USER, password=DB_PW, host=DB_HOST, port=DB_PORT)
connection.autocommit = True
bot = commands.Bot(command_prefix='/', intents=discord.Intents(guild_messages=True, message_content=True))


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


def createtable():
    cur = connection.cursor()
    cur.execute(" CREATE TABLE IF NOT EXISTS public.discordinvite ("
                "discordid VARCHAR(30) PRIMARY KEY,"
                "steamid VARCHAR(30)); ")


createtable()


def steamresponse(steamid):
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    apikey = APIKEY
    payload = {'key': apikey, 'steamids': steamid}
    response = requests.get(url, params=payload)
    jsonresponse = response.json()
    playersteamid = jsonresponse.get("response").get("players")[0].get("steamid")
    playergameid = jsonresponse.get("response").get("players")[0].get("gameid")
    playerlobbyid = jsonresponse.get("response").get("players")[0].get("lobbysteamid")
    invitelink = "steam://joinlobby/" + playergameid + "/" + playerlobbyid + "/" + playersteamid
    return invitelink


def addrecord(arg1, arg2):
    cur = connection.cursor()
    cur.execute(" SELECT * FROM discordinvite WHERE (discordid) = (%s);", (arg1,))
    if cur.fetchone() is None:
        cur.execute(" INSERT INTO discordinvite (discordid, steamid) VALUES (%s,%s);", (arg1, arg2))
        cur.close()
        return "Your Steam ID was added"
    else:
        cur.close()
        return ", This Steam ID is already registered, please use /changeid command if you would like to change it"


def removerecord(arg):
    cur = connection.cursor()
    cur.execute(" DELETE FROM discordinvite WHERE (discordid) = (%s);", (arg,))
    cur.close()
    return "Your Steam ID has been removed"


def fetchid(arg):
    cur = connection.cursor()
    cur.execute(" SELECT (steamid) FROM discordinvite WHERE (discordid) = (%s);", (arg,))
    x = cur.fetchone()[0]
    cur.close()
    return x


def updateid(arg1, arg2):
    cur = connection.cursor()
    print(arg1 + " " + arg2)
    cur.execute(" UPDATE discordinvite SET steamid = (%s) WHERE discordid = (%s);", (arg2, arg1))
    cur.close()
    return "Your Steam ID has been updated"


@bot.command(name='lobby')
async def lobby(ctx):
    discord_id = str(ctx.message.author.id)
    steamid = fetchid(discord_id)
    res = steamresponse(steamid)
    button1 = discord.ui.Button(style=discord.ButtonStyle.green,
                                url="https://gauntlet36.github.io/lobby.html?target=" + res, label="Join")
    view = discord.ui.View()
    view.add_item(button1)
    # embed = discord.Embed(title="Join OJay's Lobby", url="https://gauntlet36.github.io/lobby.html?target=" + res,
    #                       description="Join OJay's Lobby",
    #                       color=0xFF5733)
    if ctx.message.author.nick is None:
        await ctx.send("Join " + str(ctx.message.author) + "'s lobby", view=view)
    else:
        await ctx.send("Join " + str(ctx.message.author.nick) + "'s lobby", view=view)


@bot.command(name='register', pass_context=True)
async def register(ctx, arg):
    await ctx.message.delete()
    discord_id = str(ctx.message.author.id)
    steam_id = str(arg)
    response = addrecord(discord_id, steam_id)
    if ctx.message.author.nick is None:
        await ctx.send("Thanks " + str(ctx.message.author) + " " + response)
    else:
        await ctx.send("Thanks " + str(ctx.message.author.nick) + " " + response)


@bot.command(name='unregister', pass_context=True)
async def unregister(ctx):
    discord_id = str(ctx.message.author.id)
    response = removerecord(discord_id)
    if ctx.message.author.nick is None:
        await ctx.send("Thanks " + str(ctx.message.author) + " " + response)
    else:
        await ctx.send("Thanks " + str(ctx.message.author.nick) + " " + response)


@bot.command(name='checkid', pass_context=True)
async def checkid(ctx):
    discord_id = str(ctx.message.author.id)
    steamid = fetchid(discord_id)
    await ctx.author.send("Your registered steam ID is " + steamid)


@bot.command(name='changeid', pass_context=True)
async def changeid(ctx, arg):
    discord_id = str(ctx.message.author.id)
    steam_id = arg
    response = updateid(discord_id, steam_id)
    if ctx.message.author.nick is None:
        await ctx.send("Thanks " + str(ctx.message.author) + " " + response)
    else:
        await ctx.send("Thanks " + str(ctx.message.author.nick) + " " + response)


@bot.command(name='lobbyhelp')
async def lobbyhelp(ctx):
    helpmessage = """This bot can be used to send invite links automatically
    In order for it to work, you must have your steam profile public and register your steam ID.
    You can find your steam ID by going to your steam community profile. If you have a custom URL you can enter the name
    after id into https://www.steamidfinder.com/ to find your steam ID.
    Also see Steam FAQ here https://help.steampowered.com/en/faqs/view/2816-BE67-5B69-0FEC
    
    The commands that you can use are:
    
    **/register *STEAMID*** - This adds your Steam ID to the database
    **/lobby** - If you\'ve registered your Steam ID and are currently in a joinable lobby. This will post a link"""

    embed = discord.Embed(title="Help", description=helpmessage, color=0xFF5733)
    await ctx.send(embed=embed)

bot.run(TOKEN)
