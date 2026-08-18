import discord
from discord import app_commands
from pathlib import Path
import random


@app_commands.command(name="szabi", description="Random Szabi image")
async def szabi(interaction: discord.Interaction):
    images_dir = Path(__file__).resolve().parent.parent / "images"
    if not images_dir.exists():
        await interaction.response.send_message("Images directory not found.", ephemeral=True)
        return
    files = [p for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".gif", ".webp")]
    if not files:
        await interaction.response.send_message("No images found.", ephemeral=True)
        return
    selected = random.choice(files)
    await interaction.response.send_message(file=discord.File(str(selected)))
