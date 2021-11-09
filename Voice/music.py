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
        if song is None:
            return await ctx.send("Akta gaan to bolbi!?!")

        if ctx.voice_client is None:
            return await ctx.send("Amare akta channel e dhuka daoat dia (*join)")
                

        # handle song where song isn't url
        if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
            await ctx.send("Dara mama, gaan ta khujtesi")

            result = await self.search_song(1, song, get_url=True)

            if result is None:
                return await ctx.send(
                    "Mama gaan khuijja pai nai :("
                )

            song = result[0]

        if ctx.voice_client.source is not None:
            queue_len = len(self.song_queue[ctx.guild.id])

            if queue_len < 100:
                self.song_queue[ctx.guild.id].append(song)
                return await ctx.send(
                    f"Mama Gaan ta Queue te add kore disi ai → {queue_len+1} position e."
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

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("Ami kono gaan bajaitesi na")

        if ctx.author.voice is None:
            return await ctx.send("Age akta voice channel e dhuk!")

        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("Onno channel theke gaan skip korte parbi na!!!")
                

        # poll = discord.Embed(
        #     title=
        #     f"Vote to Skip Song by - {ctx.author.name}#{ctx.author.discriminator}",
        #     description=
        #     "**80% of the voice channel must vote to skip for it to pass.**",
        #     colour=discord.Colour.blue())
        # poll.add_field(name="Skip", value=":white_check_mark:")
        # poll.add_field(name="Stay", value=":no_entry_sign:")
        # poll.set_footer(text="Voting ends in 15 seconds.")

        # poll_msg = await ctx.send(
        #     embed=poll
        # )  # only returns temporary message, we need to get the cached message to get the reactions
        # poll_id = poll_msg.id

        # await poll_msg.add_reaction(u"\u2705")  # yes
        # await poll_msg.add_reaction(u"\U0001F6AB")  # no

        # await asyncio.sleep(15)  # 15 seconds to vote

        # poll_msg = await ctx.channel.fetch_message(poll_id)

        # votes = {u"\u2705": 0, u"\U0001F6AB": 0}
        # reacted = []

        # for reaction in poll_msg.reactions:
        #     if reaction.emoji in [u"\u2705", u"\U0001F6AB"]:
        #         async for user in reaction.users():
        #             if user.voice.channel.id == ctx.voice_client.channel.id and user.id not in reacted and not user.bot:
        #                 votes[reaction.emoji] += 1

        #                 reacted.append(user.id)

        # skip = False

        # if votes[u"\u2705"] > 0:
        #     if votes[u"\U0001F6AB"] == 0 or votes[u"\u2705"] / (
        #             votes[u"\u2705"] +
        #             votes[u"\U0001F6AB"]) > 0.79:  # 80% or higher
        #         skip = True
        #         embed = discord.Embed(
        #             title="Skip Successful",
        #             description=
        #             "***Voting to skip the current song was succesful, skipping now.***",
        #             colour=discord.Colour.green())

        # if not skip:
        #     embed = discord.Embed(
        #         title="Skip Failed",
        #         description=
        #         "*Voting to skip the current song has failed.*\n\n**Voting failed, the vote requires at least 80% of the members to skip.**",
        #         colour=discord.Colour.red())

        # embed.set_footer(text="Voting has ended.")

        # await poll_msg.clear_reactions()
        # await poll_msg.edit(embed=embed)

        # if skip:
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


async def setup():
    await bot.wait_until_ready()
    bot.add_cog(Player(bot))


bot.loop.create_task(setup())

bot.run(os.environ.get("TOKEN"))

