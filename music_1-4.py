import youtube_dl
import pafy
import discord
from discord.ext import commands
from pytube import Playlist

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="*", intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user.name} is ready.")


class SongItem:
    def __init__(self, name, url, youtube_url):
        self.song_name = name
        self.song_url = url
        self.youtube_url = youtube_url


class Player(commands.Cog):
    def __init__(self, discord_bot):
        self.bot = discord_bot
        self.song_queue = {}
        self.repeat = {}
        self.current_song = {}

        self.setup()

    def setup(self):
        for guild in self.bot.guilds:
            self.song_queue[guild.id] = []
            self.repeat[guild.id] = False
            self.current_song[guild.id] = {}

    async def check_queue(self, ctx):
        if self.repeat[ctx.guild.id]:
            await self.play_song(ctx, self.current_song[ctx.guild.id])
        elif len(self.song_queue[ctx.guild.id]) > 0:
            await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
            self.song_queue[ctx.guild.id].pop(0)
        else:
            if ctx.voice_client is not None:
                await ctx.send("Mama gaan shonano shesh gelam ga!")
                self.current_song[ctx.guild.id] = {}
                return await ctx.voice_client.disconnect()

    async def search_song(self, amount, song, get_url=False):
        info = await self.bot.loop.run_in_executor(
            None, lambda: youtube_dl.YoutubeDL({
                "format": "bestaudio",
                "quiet": True
            }).extract_info(f"ytsearch{amount}:{song}",
                            download=False,
                            ie_key="YoutubeSearch"))
        if len(info["entries"]) == 0:
            return None

        return [entry["webpage_url"]
                for entry in info["entries"]] if get_url else info

    async def play_song(self, ctx, song):
        self.current_song[ctx.guild.id] = song
        await ctx.send(f"Akhon ami ai gaan → {self.current_song[ctx.guild.id].song_name} gaitesi 🎶")
        url = song.song_url
        ctx.voice_client.play(discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(url)),
            after=lambda error: self.bot.loop.create_task(
                self.check_queue(ctx)))
        ctx.voice_client.source.volume = 0.5

    # Joins the channel
    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send(
                "Age Akta Voice Channel e Dhuk!"
            )

        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()

        await ctx.author.voice.channel.connect()

    # Leaves the channel
    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            return await ctx.voice_client.disconnect()

        await ctx.send("Ami to kono channel ei nai mama")

    # Plays the song via link or via text
    @commands.command()
    async def play(self, ctx, *, song=None):
        if ctx.author.voice is None:
            return await ctx.send("Age Akta Voice Channel e Dhuk!")

        if song is None:
            return await ctx.send("Akta gaan to bolbi!?!")

        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()

        # handle song where song isn't url
        if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
            await ctx.send("Dara mama, gaan ta khujtesi")

            result = await self.search_song(1, song, get_url=True)

            if result is None:
                return await ctx.send(
                    "Mama ki gaan des, khuijja pai nai :("
                )

            data = pafy.new(result[0])
            song = SongItem(data.title, data.getbestaudio().url, result[0])

        else:
            data = pafy.new(song)
            song = SongItem(data.title, data.getbestaudio().url, song)

        if ctx.voice_client.source is not None:
            queue_len = len(self.song_queue[ctx.guild.id])

            if queue_len < 100:
                self.song_queue[ctx.guild.id].append(song)
                return await ctx.send(
                    f"Mama {song.song_name} Gaan ta Queue te add kore disi {queue_len + 1} position e."
                )

            else:
                return await ctx.send(
                    "Mama jekhan theke churi korsi, ora 100 ta gaan porjonto limit korse and asef oita tule nai..."
                )

        await self.play_song(ctx, song)

    # Searches YouTube links for the text
    @commands.command()
    async def search(self, ctx, *, song=None):
        if song is None:
            return await ctx.send("Gaan er naam to lekhbi ?!?")

        await ctx.send("Gaan khujtesi shomoy lagte pare ._.")

        info = await self.search_song(5, song)

        embed = discord.Embed(
            title=f"Er modhe konta?",
            description="*Edi dia nijeo gaan play korte parbi kintu*\n",
            colour=discord.Colour.red())

        amount = 0
        for entry in info["entries"]:
            amount += 1
            embed.description += f"[{amount}. {entry['title']}]({entry['webpage_url']})\n"

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
        for item in self.song_queue[ctx.guild.id]:
            embed.description += f"{i}) {item.song_name}\n"
            i += 1

        embed.set_footer(text="Amake bebohar korar jonno dhonnobad >.>")
        await ctx.send(embed=embed)

    @commands.command(aliases=['stop', 'next'])
    async def skip(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("Ami kono gaan bajaitesi na")

        if ctx.author.voice is None:
            return await ctx.send("Age akta voice channel e dhuk!")

        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            return await ctx.send("Onno channel theke gaan skip korte parbi na!!!")

        ctx.voice_client.stop()
        await ctx.send("Current gaan ta bhalo lage nai?!? 👉👈")
        if self.repeat[ctx.guild.id]:
            await ctx.send("Ami kintu ekhono pechaiyai asi! 🥨")

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

    @commands.command(aliases=['clear'])
    async def clear_queue(self, ctx):
        self.song_queue[ctx.guild.id].clear()
        await ctx.send("Mama queue khali kore disi")

    # Single song repeat[ctx.guild.id] command
    @commands.command(aliases=['loop'])
    async def repeat(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send("Age Akta Voice Channel e Dhuk!")

        if ctx.voice_client is None:
            return await ctx.send("Ami to kono voice channel e nai :( Amare daoat de *join dia")

        if self.repeat[ctx.guild.id]:
            self.repeat[ctx.guild.id] = False
            await ctx.send("\"Ex o nai, pech o nai\" - Arif & Chisty")
        else:
            self.repeat[ctx.guild.id] = True
            await ctx.send("Mama gaan ta pechay disi, na chutano porjonto pechaitei thakbo!?! 🍩")

    # Get info on the current song
    @commands.command(aliases=['ki_baje?', 'ki_baje', 'gaan', 'current'])
    async def current_song(self, ctx):
        if ctx.voice_client is None:
            return await ctx.send("Daoat na diye khoj khobor jante chaoa bhalo jinish na. 😤🤐")
        if not self.current_song[ctx.guild.id]:
            return await ctx.send("Kono gaan e bajaitesi na! 🤡")
        if not ctx.voice_client.is_paused() or ctx.voice_client.is_paused:
            embed = discord.Embed(
                title="Bot Message",
                description="Song Name, Link",
                colour=discord.Colour.blurple())
            embed.add_field(name="__Current Song__",
                            value=f"Name: {self.current_song[ctx.guild.id].song_name}\n"
                                  f"Url: {self.current_song[ctx.guild.id].youtube_url}",
                            inline=False)
            return await ctx.send(embed=embed)

    # Play Playlist
    @commands.command()
    async def playlist(self, ctx, *, playlist):
        if ctx.author.voice is None:
            return await ctx.send("Age Akta Voice Channel e Dhuk!")

        if playlist is None:
            return await ctx.send("Ahhaaaaa!!! Akta playlist dhalte hobe to!?!")

        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()

        playlist = Playlist(playlist)
        try:
            if len(playlist) <= 0:
                return await ctx.send("Thik moton link de! 👿")

            for item in playlist:
                data = pafy.new(item)
                self.song_queue[ctx.guild.id].append(SongItem(data.title, data.getbestaudio().url, item))

            await ctx.send(f"{len(playlist)} ta gaan queue te add kore disi 🥳")

            if not self.current_song[ctx.guild.id]:
                await self.check_queue(ctx)
        except KeyError:
            return await ctx.send("Thik moton link de! 👿")

    @commands.command()
    async def remove(self, ctx, number="-1"):
        if not number.isnumeric():
            return await ctx.send("Thik moton bol kon gaan remove korbo?!?")

        if 0 < int(number) <= len(self.song_queue[ctx.guild.id]):
            item = self.song_queue[ctx.guild.id].pop(int(number) - 1)
            return await ctx.send(f"{number} no. gaan, {item.song_name} ta remove kore disi")

        return await ctx.send(f"{number} no. gaan queue list ei nai? Ki kos na kos?!?")

    # Bring a specific song to the front
    @commands.command(aliases=['playnext', 'play_next', 'playNext'])
    async def bring_to_front(self, ctx, number="-1"):
        if not number.isnumeric():
            return await ctx.send("Thik moton bol kon gaan shamne anbo?!?")

        if 0 < int(number) <= len(self.song_queue[ctx.guild.id]):
            item = self.song_queue[ctx.guild.id].pop(int(number) - 1)
            self.song_queue[ctx.guild.id].insert(0, item)
            return await ctx.send(f"{number} no. gaan, {item.song_name} next e bajbe")

        return await ctx.send(f"{number} no. gaan queue list ei nai? Ki kos na kos?!?")

    # Help Command
    @commands.command(aliases=['halp'])
    async def shahajjo(self, ctx):
        embed = discord.Embed(
            title="Help",
            description="",
            colour=discord.Colour.dark_gold())
        embed.add_field(name="__Commands__",
                        value="*play <url/name> - Oi gaan ta shunabo othoba queue te dhele dibo\n"
                              "*join - Bot channel e join korbe\n"
                              "*leave - Bot channel theke bair hoye jaibo\n"
                              "*queue - Akhon current queue te ki ki ase eta dekhabo\n"
                              "*(skip/stop/next) - Current gaan ta skip kore dibo\n"
                              "*pause - Gaan gaoa thamay boshe thakbo\n"
                              "*resume - Abar gaan gaoa shuru korbo\n"
                              "*(clear_queue/clear) - Pura queue khali kore rekhe dibo\n"
                              "*(repeat/loop) - Current gaan ta loop e cholte thakbe, abar likhle off hoye jabe\n"
                              "*(current_song/ki_baje?/ki_baje/gaan/current) - Current gaan er nam, link bole dibo\n"
                              "*playlist <url> - Oi link er shate jotto gaan ase shob queue te add kore dibo\n"
                              "*remove <Number> - Oi number gaan ta remove kore dibo\n"
                              "*(bring_to_front/playnext/play_next/playNext) <Number> - Oi number gaan ta remove kore "
                              "dibo\n "                              
                              "*search <name> - Gaan tar jonno bivinno link ber kore dibo\n"
                              "*shahajjo - Ai message tai dekhabo",
                        inline=False)
        await ctx.send(embed=embed)

        async def create_db_pool(self): # making it a bound function in my example
            database_url = ''
            self.pg_con = await asyncpg.create_pool(database_url, ssl="require")

        async def setup_hook(self):
            await self.create_db_pool()


async def setup():
    await bot.wait_until_ready()
    bot.add_cog(Player(bot))


bot.loop.create_task(setup())

#bot.run(YOUR KEY HERE)
