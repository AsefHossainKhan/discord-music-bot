import discord
from discord.ext import commands
import youtube_dl
import os
import urllib.request
from bs4 import BeautifulSoup
import time


client = commands.Bot(command_prefix="*")

#region check commands
def is_connected(ctx):
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()

def is_playing(ctx):
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_playing()

def voice_client(ctx):
    return discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

#endregion

#region Queue Part
class yt:
  def __init__(self, title, url): 
    self.title = title 
    self.url = url

myQueue = []

async def play_next(ctx):
    if (len(myQueue) == 0):
        await ctx.send("mama toder ar gaan shunamu na ami gelam ga")
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        if voice.is_connected():
            await voice.disconnect()
    else:
        current_song = myQueue.pop(0)
        await play(ctx, current_song.url)
#endregion

#region commands
@client.command()
async def test(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice is None:
        await ctx.author.voice.channel.connect()


@client.command()
async def list(ctx):
    if (len(myQueue) == 0):
        await ctx.send("mama kono gaan nai queue te")
        return
    listString = "```"
    for index, item in enumerate(myQueue):
        listString += (f"{index+1}. {item.title} \n")
    listString += "```"
    await ctx.send(listString)


@client.command()
async def play(ctx, url : str):

    current_song_name = BeautifulSoup(urllib.request.urlopen(url).read().decode("utf-8"), features="lxml")
    current_song_name = str(current_song_name.title)[7:-8]
    if is_playing(ctx):
        myQueue.append(yt(current_song_name,url))
        await ctx.send("Mama Gaan ta queue te add kore disi, aitar porei play hobe")
        return
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Gaan Shesh houar jonno wait kor naile stop kor with *stop !!!")
        return

    # voiceChannel = discord.utils.get(ctx.guild.voice_channels, name='Music Palace')
    if ctx.author.voice is None:
        await ctx.send("Age Akta Voice Channel e Dhuk!")
    voiceChannel = ctx.author.voice.channel
    if not is_connected(ctx):
        await voiceChannel.connect(reconnect=True)
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, "song.mp3")


    await ctx.send(f"Mama ami akhon ai gaan gaitesi 🎶 → {current_song_name}")
    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: ctx.bot.loop.create_task(play_next(ctx)))
    


@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("Bot kono Channel e nai!")


@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Kono Gaan Baje Na")


@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("Gaan to paused na, resume kemne korum")


@client.command()
async def skip(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()

@client.command()
async def clear_queue(ctx):
    myQueue.clear()
    await ctx.send("Mama queue khali kore disi")

#endregion

client.run(os.environ.get("TOKEN"))