import requests
import discord
from discord import app_commands

url = "https://official-joke-api.appspot.com/jokes/random"

def getjoke():
    data = (requests.get(url).json())
    print(data)
    return data 

getjoke()

@app_commands.command(
    name="tellmeajoke",
    description="I'll tell you a hilarious joke"
)
async def joke(interaction: discord.Interaction):
    data = getjoke()

    await interaction.response.send_message(
        f"- {data['id']}\n"
        f"- {data['setup']}\n"
        f"- {data['punchline']}"
    )
