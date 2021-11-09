import discord
from discord.ext import commands
from test import Player
import os

intents = discord.Intents.default()
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
  print("READY")

async def setup():
  await bot.wait_until_ready()
  bot.add_cog(Player(bot))

bot.loop.create_task(setup())

bot.run(os.environ.get("TOKEN"))
