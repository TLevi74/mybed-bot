import asyncio

import discord
import requests
from discord import app_commands


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_weather(city: str):
    location_response = requests.get(
        GEOCODING_URL,
        params={"name": city, "count": 1, "language": "hu", "format": "json"},
        timeout=10,
    )
    location_response.raise_for_status()
    locations = location_response.json().get("results", [])

    if not locations:
        raise ValueError(f"Nem található ilyen város: {city}")

    location = locations[0]
    weather_response = requests.get(
        FORECAST_URL,
        params={
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "daily": (
                "temperature_2m_max,temperature_2m_min,sunrise,sunset,"
                "weather_code"
            ),
            "current": (
                "temperature_2m,rain,relative_humidity_2m,"
                "wind_speed_10m,weather_code"
            ),
            "timezone": "auto",
        },
        timeout=10,
    )
    weather_response.raise_for_status()
    return location, weather_response.json()


def value_with_unit(name, value, units):
    unit = units.get(name, "")
    return f"{value} {unit}".strip()


class WeatherModal(discord.ui.Modal, title="Időjárás lekérése"):
    city = discord.ui.TextInput(
        label="Melyik város időjárása érdekel?",
        placeholder="Például: Budapest",
        min_length=2,
        max_length=100,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        try:
            location, data = await asyncio.to_thread(fetch_weather, self.city.value)
        except ValueError as error:
            await interaction.followup.send(str(error), ephemeral=True)
            return
        except requests.RequestException:
            await interaction.followup.send(
                "Az időjárási szolgáltatás most nem érhető el. Próbáld újra később!",
                ephemeral=True,
            )
            return

        place = ", ".join(
            part
            for part in (location.get("name"), location.get("admin1"), location.get("country"))
            if part
        )
        main_embed = discord.Embed(
            title=f"🌦️ Időjárás – {place}",
            color=discord.Color.blue(),
        )
        main_embed.add_field(
            name="Hely és API-adatok",
            value=(
                f"Szélesség: `{data['latitude']}`\n"
                f"Hosszúság: `{data['longitude']}`\n"
                f"Tengerszint feletti magasság: `{data['elevation']} m`\n"
                f"Időzóna: `{data['timezone']}` ({data['timezone_abbreviation']})\n"
                f"UTC-eltérés: `{data['utc_offset_seconds']} s`\n"
                f"Generálási idő: `{data['generationtime_ms']:.2f} ms`"
            ),
            inline=False,
        )

        current = data["current"]
        current_units = data["current_units"]
        current_lines = [
            f"{name}: `{value_with_unit(name, value, current_units)}`"
            for name, value in current.items()
        ]
        main_embed.add_field(
            name="Jelenlegi adatok",
            value="\n".join(current_lines),
            inline=False,
        )

        daily = data["daily"]
        daily_units = data["daily_units"]
        daily_embeds = []
        for index, date in enumerate(daily["time"]):
            lines = [
                f"{name}: `{value_with_unit(name, values[index], daily_units)}`"
                for name, values in daily.items()
                if name != "time"
            ]
            daily_embeds.append(
                discord.Embed(
                    title=f"📅 {date}",
                    description="\n".join(lines),
                    color=discord.Color.light_grey(),
                )
            )

        await interaction.followup.send(embeds=[main_embed, *daily_embeds])


@app_commands.command(name="weather", description="Időjárás lekérése egy városhoz")
async def weather(interaction: discord.Interaction):
    await interaction.response.send_modal(WeatherModal())
