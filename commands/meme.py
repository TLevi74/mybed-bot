import discord
from discord import app_commands
import aiohttp
import random


@app_commands.command(name="meme", description="Random meme")
async def meme(interaction: discord.Interaction):

    url = "https://www.reddit.com/r/memes/hot.json?limit=50"

    headers = {
        "User-Agent": "MyDiscordBot/1.0"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:

            if response.status != 200:
                await interaction.response.send_message(
                    "Couldn't get a meme right now."
                )
                return

            data = await response.json()

    posts = data["data"]["children"]

    images = []

    for post in posts:
        post_data = post["data"]

        if post_data.get("post_hint") == "image":
            images.append(post_data)

    if not images:
        await interaction.response.send_message(
            "Couldn't find a meme right now."
        )
        return

    meme = random.choice(images)

    embed = discord.Embed(
        title=meme["title"],
        url="https://reddit.com" + meme["permalink"]
    )

    embed.set_image(url=meme["url"])

    await interaction.response.send_message(embed=embed)