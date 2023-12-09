import os
import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv
import sqlite3

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
DB_NAME = os.getenv('DB_NAME')
API_KEY = os.getenv('API_KEY')

connection = sqlite3.connect(DB_NAME, autocommit=True)
bot = commands.Bot(command_prefix='/', intents=discord.Intents(guild_messages=True, message_content=True))


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


def createtable():
    cur = connection.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS discordinvite ("
                "discordid TEXT PRIMARY KEY,"
                "steamid TEXT); ")
    cur.close()

createtable()

def steamresponse(steamid):
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    apikey = API_KEY
    payload = {'key': apikey, 'steamids': steamid}
    response = requests.get(url, params=payload)
    jsonresponse = response.json()
    playersteamid = jsonresponse.get("response").get("players")[0].get("steamid")
    playergameid = jsonresponse.get("response").get("players")[0].get("gameid")
    playerlobbyid = jsonresponse.get("response").get("players")[0].get("lobbysteamid")
    invitelink = "steam://joinlobby/" + playergameid + "/" + playerlobbyid + "/" + playersteamid
    return invitelink


def steamidresponse(vanityurl):
    url = "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/"
    apikey = API_KEY
    payload = {'key': apikey, 'vanityurl': vanityurl}
    response = requests.get(url, params=payload)
    jsonresponse = response.json()
    playersteamid = jsonresponse.get("response").get("steamid")
    return playersteamid


def addrecord(arg1, arg2):
    cur = connection.cursor()
    cur.execute("SELECT * FROM discordinvite WHERE (discordid) = (?);", (arg1,))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO discordinvite (discordid, steamid) VALUES (?,?);", (arg1, arg2))
        cur.close()
        return "Your Steam ID was added"
    else:
        cur.close()
        return ", This Steam ID is already registered, please use /changeid command if you would like to change it"


def tempforceaddrecord(arg1, arg2):
    cur = connection.cursor()
    cur.execute("SELECT * FROM discordinvite WHERE (discordid) = (?);", (arg1,))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO discordinvite (discordid, steamid) VALUES (?,?);", (arg1, arg2))
        cur.close()
        return True
    else:
        cur.close()
        return False


def removerecord(arg):
    cur = connection.cursor()
    cur.execute("DELETE FROM discordinvite WHERE (discordid) = (?);", (arg,))
    cur.close()
    return "Your Steam ID has been removed"


def fetchid(arg):
    cur = connection.cursor()
    cur.execute("SELECT (steamid) FROM discordinvite WHERE (discordid) = (?);", (arg,))
    x = cur.fetchone()[0]
    cur.close()
    return x


def updateid(arg1, arg2):
    cur = connection.cursor()
    cur.execute("UPDATE discordinvite SET steamid = (?) WHERE discordid = (?);", (arg2, arg1))
    cur.close()
    return "Your Steam ID has been updated"


@bot.event
async def on_message(message):

    if message.author == bot.user:
        return
    steamcheck = message.content
    if steamcheck.startswith("steam://joinlobby/"):
        steamsplit = steamcheck.split(" ", maxsplit=1)
        steamlink = steamsplit[0]
        if 50 <= len(steamlink) <= 75:
            ctx = await bot.get_context(message)
            button1 = discord.ui.Button(style=discord.ButtonStyle.green,
                                        url="https://gauntlet36.github.io/lobby.html?target=" + steamlink, label="Join")
            view = discord.ui.View()
            view.add_item(button1)
            await ctx.send("Join " + str(ctx.message.author.display_name) + "'s lobby", view=view)
            discord_id = str(ctx.message.author.id)
            steam_id = steamlink.split("/")
            steam_id = steam_id[-1]
            steam_id = steam_id[:17]
            if steam_id.isnumeric():
                if tempforceaddrecord(discord_id,steam_id):
                    response = "Your Steam ID was added. If your steam profile is public In the future you can use the" \
                        " /lobby command to automatically create an invite link"
                    await ctx.send(response)
    await bot.process_commands(message)


@bot.command(name='lobby')
async def lobby(ctx):
    discord_id = str(ctx.message.author.id)
    steamid = fetchid(discord_id)
    res = steamresponse(steamid)
    button1 = discord.ui.Button(style=discord.ButtonStyle.green,
                                url="https://gauntlet36.github.io/lobby.html?target=" + res, label="Join")
    view = discord.ui.View()
    view.add_item(button1)
    await ctx.send("Join " + str(ctx.message.author.display_name) + "'s lobby", view=view)


@bot.command(name='register', pass_context=True)
async def register(ctx, arg):
    #await ctx.message.delete()
    discord_id = str(ctx.message.author.id)
    if arg.startswith("https://steamcommunity.com/id/"):
        argsplit = arg.split("id/")
        vanityid = argsplit[1].strip("/")
        steam_id = steamidresponse(vanityid)
        if steam_id.isnumeric():
            response = addrecord(discord_id, steam_id)
            await ctx.send("Thanks " + str(ctx.message.author.display_name) + response)
        else:
            await ctx.send("The Steam profile URL you entered may be invalid")

    if arg.startswith("https://steamcommunity.com/profiles/"):
        argsplit = arg.split("profiles/")
        steam_id = argsplit[1]
        steam_id = steam_id[:17]
        if steam_id.isnumeric():
            response = addrecord(discord_id, steam_id)
            await ctx.send("Thanks " + str(ctx.message.author.display_name) + " " + response)
        else:
            await ctx.send("The Steam profile URL you entered may be invalid")


@bot.command(name='unregister', pass_context=True)
async def unregister(ctx):
    discord_id = str(ctx.message.author.id)
    response = removerecord(discord_id)
    await ctx.send("Thanks " + str(ctx.message.author.display_name) + " " + response)


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
    await ctx.send("Thanks " + str(ctx.message.author.display_name) + " " + response)


@bot.command(name='lobbyhelp')
async def lobbyhelp(ctx):
    helpmessage = "I can help you send invite links automatically. In order to work, you must "\
            "have a public Steam profile and register your Steam ID with me.\n\n"\
            \
            "To register your ID, simply use the register command with your full steam "\
            "profile URL "\
            \
            "The commands that you can use are:\n\n"\
            \
            "**/register *SteamProfileURL*** - This adds your Steam ID to the database\n"\
            "**/lobby** - If you've registered your Steam ID and are currently in a joinable "\
                         "lobby, this will post a link"

    embed = discord.Embed(title="Help", description=helpmessage, color=0xFF5733)
    await ctx.send(embed=embed)

bot.run(TOKEN)
