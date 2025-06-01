# Dennis Goomba

version = "0.1"
configDir = "config"
sqldb = "databases/main.db"

import discord
from discord import app_commands
from discord.ext import tasks, commands
import json
from glob import glob
import random
import sqlite3

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="*", intents=intents)

confs = {}

con = sqlite3.connect(sqldb)

for fn in glob(configDir+"/*.json"):
    with open(fn) as f:
        index = fn.replace(configDir+"/", "")
        index = index.replace(".json", "")
        print(f"Loading config file '{index}' ({fn})...")
        confs[index] = json.load(f)

def get_rank(coins):
    # order highest to lowest, except for debt
    # TODO: move to a .json config file
    if coins < 0:
        return "how are you in debt :house_abandoned::wilted_rose:"
    elif coins >= 130:
        return "<:squat:1284655672600039597><:squat:1284655672600039597><:squat:1284655672600039597> *Landillionaire* <:squat:1284655672600039597><:squat:1284655672600039597><:squat:1284655672600039597>"
    elif coins >= 90:
        return ":fire:<:frog:1312666151142031380> SHANGHAI SCAMMER <:frog:1312666151142031380>:fire:"
    elif coins >= 70:
        return "<:blee:1312666042438258739> BLEE-BILLIONAIRE <:blee:1312666042438258739>"
    elif coins >= 50:
        return "RAT RACER :cheese::rat:"
    elif coins >= 30:
        return "Free_Money.exe runner :money_mouth:"
    elif coins >= 10:
        return "money's good if money's great <:deer:1312666403844653136>"
    elif coins >= 1:
        return "lil buck"
    else:
        return "broke, but just you watch"

def db_request(con, request, commit=False, params=tuple()):
    cur = con.cursor()
    res = cur.execute(request, params)
    if commit:
        con.commit()
    return res

def db_prepare():
    db_request(con, "CREATE TABLE IF NOT EXISTS bleecoin(userid INT UNIQUE, amount INT)")

def get_bleecoins(userid):
    res = db_request(con, "SELECT amount FROM bleecoin WHERE userid = ?", False, (userid, ))
    bcres = res.fetchone()
    if bcres is None: # user doesn't have entry in database
        bleecoins = 0
    else:
        bleecoins = bcres[0]
    return bleecoins

@client.tree.command(name = "quote", description = "Get a random Kyle Landon quote.")
async def quote_command(ctx):
    quote = random.choice(confs["quotes"])
    quote = quote.replace("{user.mention}", f"{ctx.user.mention}")
    await ctx.response.send_message(f"{quote}")

@client.tree.command(name = "leaderboard", description = "Check the bleecoin leaderboard.")
async def leaderboard_command(ctx):
    res = db_request(con, "SELECT userid, amount FROM bleecoin WHERE amount != 0 ORDER BY amount DESC LIMIT 11")
    entries = res.fetchall()
    lbtext = ""
    i = 1
    for entry in entries:
        #user = await client.fetch_user(entry[0])
        #if user == None:
        #    continue
        userid = entry[0]
        if userid == client.user.id:
            continue
        coins = entry[1]
        if userid == 1115089770129932359:
            emoji = ":foot:"
        else:
            emoji = confs["main"]["bleecoin-emoji"]
        if i == 1:
            lbtext = lbtext+"### :first_place: "
        elif i == 2:
            lbtext = lbtext+"### :second_place: "
        elif i == 3:
            lbtext = lbtext+"### :third_place: "
        elif i == 11:
            lbtext = lbtext+f"-# honourable mention: <@!{userid}>, {coins} coins."
        else:
            lbtext = lbtext+f"**{i}.** "
        if i != 11:
            lbtext = lbtext+f"<@!{userid}> • {coins} {emoji} ({get_rank(coins)})\n"
        i=i+1
    if i == 12:
        lbtext = f"TOP 10 HUSTLAS::::::\n"+lbtext
    else:
        lbtext = f"TOP 10 ({i-1} actually) HUSTLAS::::::\n"+lbtext
    embed = discord.Embed(
        title="Bleecoin Leaderboard",
        description=lbtext
    )
    await ctx.response.send_message("", embed=embed, allowed_mentions=discord.AllowedMentions.none())

@client.tree.command(name = "wallet", description = "Check your bleecoin wallet.")
async def wallet_command(ctx, user: discord.User=None):
    emoji = confs["main"]["bleecoin-emoji"]
    if user == None:
        user = ctx.user
    if user.id == 1115089770129932359:
        # Money Feet
        emoji = ":foot:";
    if user == client.user:
        embed = discord.Embed(
            color=discord.Color.random(),
            description=f"## bleecoins: all of it "+emoji+f"\nrank: **dennis goomba himself**",
        )
        embed.set_author(name=f"{user}'s wallet", icon_url=user.avatar)
        await ctx.response.send_message(f"", embed=embed)
        return
    if user.bot:
        await ctx.response.send_message(f"bruh")
        return
    bleecoins = get_bleecoins(user.id)
    embed = discord.Embed(
        color=discord.Color.random(),
        description=f"## bleecoins: {bleecoins} "+emoji+f"\nrank: **{get_rank(bleecoins)}**",
    )
    embed.set_author(name=f"{user}'s wallet", icon_url=user.avatar)
    await ctx.response.send_message(f"", embed=embed)

@client.tree.command(name = "moneyspread", description = "flex with your bleecoins #swag")
async def moneyspread_command(ctx):
    bleecoins = get_bleecoins(ctx.user.id)
    if bleecoins <= 0:
        await ctx.response.send_message("bruh you got NOTHING :joy: :rofl:")
        return
    try:
        await ctx.response.send_message(confs["main"]["bleecoin-emoji"]*bleecoins)
    except:
        await ctx.response.send_message("you got so much money it doesn't even fit in a single message")

@client.tree.command(name = "reload", description = "Reload config files. Use filename 'all' to reload all configs.")
async def reload_command(ctx, filename: str):
    log = ""
    if filename == "all":
        for fn in glob(configDir+"/*.json"):
            with open(fn) as f:
                index = fn.replace(configDir+"/", "")
                index = index.replace(".json", "")
                print(f"Loading config file '{index}' ({fn})...")
                log = log+f"Loading config file '{index}' ({fn})...\n"
                confs[index] = json.load(f)
        await ctx.response.send_message(f"```\n{log}```")
        return
    if not filename.endswith(".json"):
        filename = f"{filename}.json"
    try:
        filepath = configDir+"/"+filename
        print(f"Loading config file '{filename}' ({filepath})...")
        log = log+f"Loading config file '{filename}' ({filepath})...\n"
        with open(filepath) as f:
            index = filename.replace(".json", "")
            confs[index] = json.load(f)
        await ctx.response.send_message(f"```\n{log}```")
        return
    except FileNotFoundError:
        log = log+f"FileNotFoundError! That config file don't exist!!!!"
        await ctx.response.send_message(f"```\n{log}```")
        return

@client.tree.command(name = "song", description = "Get a random Kyle Landon song.")
async def song_command(ctx):
    album = random.choice(confs["songs"])
    song = random.choice(album["songs"])
    await ctx.response.send_message(f"Your random song is **{song}** from the album **{album['album']}**.")

@client.tree.command(name = "trivia", description = "Get a random fun fact about Kyle Landon.")
async def trivia_command(ctx):
    key = random.randrange(0, len(confs["trivia"]))
    trivia = confs["trivia"][key]
    await ctx.response.send_message(f"FACT #{key+1}: {trivia}")

@client.event
async def on_ready():
    await client.tree.sync()
    print(f"logged in as {client.user}.")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if random.randint(0, 2000) == 1:
        await asyncio.sleep(10000)
        await message.channel.send("HOOT WIRELESS")

@client.event
#async def on_reaction_add(reaction, user):
async def on_raw_reaction_add(payload):
    message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    user = payload.member
    if str(payload.emoji) != confs["main"]["bleecoin-emoji"]:
        return
    if user == message.author:
        await message.channel.send(f"{user.mention} you're a liar and a cheat")
        return
    if message.author == client.user:
        await message.channel.send(f"{user.mention} don't bother... i already got so much bleecoin i got bleecoin 2:bangbang:")
        return
    if message.author.bot:
        await message.channel.send(f"{user.mention} you can't give the bots bleecoin. you'll make them too powerful")
        return
    print(f"{user} gave {message.author} a bleecoin!")
    cur = con.cursor()
    res = cur.execute("SELECT amount FROM bleecoin WHERE userid = ?", (message.author.id, ))
    bleecoins = res.fetchone()
    if bleecoins is None: # user doesn't have entry in database
        cur.execute("INSERT INTO bleecoin VALUES (?, 1)", (message.author.id, ))
    else:
        cur.execute("UPDATE bleecoin SET amount = ? WHERE userid = ?", [bleecoins[0] + 1, message.author.id])
    con.commit()
    print(f"we done :) check db")
    #await reaction.message.channel.send(f"wowadoodle {reaction.message.author} gon get it!!!!", reference=reaction.message)

@client.event
async def on_raw_reaction_remove(payload):
    guild = await client.fetch_guild(payload.guild_id)
    user = await guild.fetch_member(payload.user_id)
    message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    if str(payload.emoji) != confs["main"]["bleecoin-emoji"]:
        return
    if user == message.author:
        await message.channel.send(f"good. don't EVER let me catch you doing that stuff again")
        return
    if message.author == client.user:
        return
    print(f"{user} took a bleecoin from {message.author}!")
    cur = con.cursor()
    res = cur.execute("SELECT amount FROM bleecoin WHERE userid = ?", (message.author.id, ))
    bleecoins = res.fetchone()
    if bleecoins is None: # user doesn't have entry in database
        cur.execute("INSERT INTO bleecoin VALUES (?, -1)", (message.author.id, )) # debt
    else:
        cur.execute("UPDATE bleecoin SET amount = ? WHERE userid = ?", [bleecoins[0] - 1, message.author.id])
    con.commit()
    print(f"we done :) check db")

db_prepare();
client.run(confs["secret"]["discord-token"])
