import os

import discord
from discord import app_commands
from dotenv import load_dotenv

from commands.hello import hello
from commands.szabi import szabi
from commands.joke import joke
from commands.weather import weather
from commands.quote import quote
from commands.meme import meme

load_dotenv()


class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.add_command(hello)
        self.tree.add_command(szabi)
        self.tree.add_command(joke)
        self.tree.add_command(weather)
        self.tree.add_command(quote)
        self.tree.add_command(meme)
        await self.tree.sync()


client = MyClient()


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


token = os.getenv("DISCORD_TOKEN")
if not token:
    raise ValueError("DISCORD_TOKEN is not set. Add it to your .env file.")

client.run(token)
