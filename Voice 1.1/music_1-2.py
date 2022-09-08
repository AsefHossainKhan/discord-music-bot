import asyncio
import youtube_dl
import pafy
import discord
from discord.ext import commands
import urllib.request
from bs4 import BeautifulSoup
import os

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="*", intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready.")


class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}

        self.setup()

    def setup(self):
        for guild in self.bot.guilds:
            self.song_queue[guild.id] = []

    async def check_queue(self, ctx):
        if len(self.song_queue[ctx.guild.id]) > 0:
            await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
            self.song_queue[ctx.guild.id].pop(0)

        else:
            if ctx.voice_client is not None:
                await ctx.send("Mama gaan shonano shesh gelam ga!")
                return await ctx.voice_client.disconnect()
    async def search_song(self, amount, song, get_url=False):
        info = await self.bot.loop.run_in_executor(
            None, lambda: youtube_dl.YoutubeDL({
                "format": "bestaudio",
                "quiet": True
            }).extract_info(f"ytsearch{amount}:{song}",
                            download=False,
                            ie_key="YoutubeSearch"))
        if len(info["entries"]) == 0: return None

        return [entry["webpage_url"]
                for entry in info["entries"]] if get_url else info

    async def play_song(self, ctx, song):
        url = pafy.new(song).getbestaudio().url
        ctx.voice_client.play(discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(url)),
                              after=lambda error: self.bot.loop.create_task(
                                  self.check_queue(ctx)))
        ctx.voice_client.source.volume = 0.5

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send(
                "Age Akta Voice Channel e Dhuk!"
            )

        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()

        await ctx.author.voice.channel.connect()

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            return await ctx.voice_client.disconnect()

        await ctx.send("Ami to kono channel ei nai mama")

    @commands.command()
    async def play(self, ctx, *, song=None):
        if ctx.author.voice is None:
            return await ctx.send(
                "Age Akta Voice Channel e Dhuk!"
            )

        if song is None:
            return await ctx.send("Akta gaan to bolbi!?!")

        if ctx.voice_client is None:
            # return await ctx.send("Amare akta channel e dhuka daoat dia (*join)")
            await ctx.author.voice.channel.connect()
                

        # handle song where song isn't url
        if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
            await ctx.send("Dara mama, gaan ta khujtesi")

            result = await self.search_song(1, song, get_url=True)

            if result is None:
                return await ctx.send(
                    "Mama ki gaan des, khuijja pai nai :("
                )

            song = result[0]

        if ctx.voice_client.source is not None:
            queue_len = len(self.song_queue[ctx.guild.id])

            if queue_len < 100:
                self.song_queue[ctx.guild.id].append(song)
                current_song_name = BeautifulSoup(urllib.request.urlopen(song).read().decode("utf-8"), features="lxml")
                current_song_name = str(current_song_name.title)[7:-8]
                return await ctx.send(
                    f"Mama {current_song_name} Gaan ta Queue te add kore disi {queue_len+1} position e."
                )

            else:
                return await ctx.send(
                    "Mama jekhan theke churi korsi, ora 100 ta gaan porjonto limit korse and asef oita tule nai..."
                )

        await self.play_song(ctx, song)
        current_song_name = BeautifulSoup(urllib.request.urlopen(song).read().decode("utf-8"), features="lxml")
        current_song_name = str(current_song_name.title)[7:-8]
        await ctx.send(f"Akhon ami ai gaaan → {current_song_name} gaitesi 🎶🎵🎼")

    @commands.command()
    async def search(self, ctx, *, song=None):
        if song is None:
            return await ctx.send("Gaan er naam to lekhbi ?!?")

        await ctx.send("Gaan khujtesi shomoy lagte pare ._.")

        info = await self.search_song(5, song)

        embed = discord.Embed(
            title=f"Er modhe konta?",
            description=
            "*Edi dia nijeo gaan play korte parbi kintu*\n",
            colour=discord.Colour.red())

        amount = 0
        for entry in info["entries"]:
            embed.description += f"[{entry['title']}]({entry['webpage_url']})\n"
            amount += 1

        embed.set_footer(text=f"Prothom {amount} ta dekhaitesi")
        await ctx.send(embed=embed)

    @commands.command()
    async def queue(self, ctx):  # display the current guilds queue
        if len(self.song_queue[ctx.guild.id]) == 0:
            return await ctx.send("Ar kono Gaan nai queue te")

        embed = discord.Embed(title="Gaan er list",
                              description="",
                              colour=discord.Colour.dark_gold())
        i = 1
        for url in self.song_queue[ctx.guild.id]:
            current_song_name = BeautifulSoup(urllib.request.urlopen(url).read().decode("utf-8"), features="lxml")
            current_song_name = str(current_song_name.title)[7:-8]
            embed.description += f"{i}) {current_song_name}\n"

            i += 1

        embed.set_footer(text="Amake bebohar korar jonno dhonnobad >.>")
        await ctx.send(embed=embed)

    @commands.command(aliases=['stop'])
    async def skip(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("Ami kono gaan bajaitesi na")

        if ctx.author.voice is None:
            return await ctx.send("Age akta voice channel e dhuk!")

        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("Onno channel theke gaan skip korte parbi na!!!")

        ctx.voice_client.stop()

    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client.is_paused():
            return await ctx.send("Ami already thaimma asi.")

        ctx.voice_client.pause()
        await ctx.send("Jah! Gaan gaoa thamay dilam")

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("Ami to kono voice channel e nai :( Amare daoat de *join dia")

        if not ctx.voice_client.is_paused():
            return await ctx.send("Ami to already gaitesi")

        ctx.voice_client.resume()
        await ctx.send("Abar gaan gaoa shuru korlam")

    @commands.command()
    async def clear_queue(self, ctx):
        self.song_queue[ctx.guild.id].clear()
        await ctx.send("Mama queue khali kore disi")


    # Help Command
    @commands.command()
    async def shahajjo(self, ctx):
        embed = discord.Embed(
            title="Help",
            description="",
            colour=discord.Colour.dark_gold())
        embed.add_field(name="__Commands__",
                        value="*play <url> - Oi gaan ta shunabo othoba queue te dhele dibo\n*queue - Akhon current queue te ki ki ase eta dekhabo\n*skip / *stop - Current gaan ta skip kore dibo\n*pause - Gaan gaoa thamay boshe thakbo\n*resume - Abar gaan gaoa shuru korbo\n*clear_queue - Pura queue khali kore rekhe dibo\n*shahajjo - Ai message tai dekhabo",
                        inline=False)
        await ctx.send(embed=embed)


async def setup():
    await bot.wait_until_ready()
    bot.add_cog(Player(bot))


bot.loop.create_task(setup())

# bot.run(os.environ.get("TOKEN"))
bot.run("ODkzMTE2NDY2MDc1OTMwNjM0.YVWxhg.-QknPhHlTz6wXLOD1p7bZ5S-Ak0")
