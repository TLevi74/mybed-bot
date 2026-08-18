import discord
from discord import app_commands
import aiohttp
import random


@app_commands.command(name="meme", description="Random meme")
async def meme(interaction: discord.Interaction):

    await interaction.response.defer()

    url = "https://meme-api.com/gimme"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:

                if response.status != 200:
                    await interaction.followup.send(
                        "Couldn't get a meme right now."
                    )
                    return

                data = await response.json()

        image_url = data["url"]
        title = data["title"]

        embed = discord.Embed(title=title)
        embed.set_image(url=image_url)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        print("ERROR:", repr(e))

        await interaction.followup.send(
            "Something went wrong while getting the meme."
        )