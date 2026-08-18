import math
import urllib.parse

import discord
import requests
from discord import app_commands


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

HEADERS = {
    "User-Agent": "mybed-discord-bot/1.0"
}


def calculate_distance(lat1, lon1, lat2, lon2):
    """Két koordináta légvonalbeli távolsága km-ben."""
    earth_radius = 6371

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius * c


def get_coordinates(place_name):
    """Szöveges helyből koordinátát készít Nominatimmel."""

    params = {
        "q": place_name,
        "format": "json",
        "limit": 1,
        "countrycodes": "hu"
    }

    response = requests.get(
        NOMINATIM_URL,
        params=params,
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if not data:
        return None

    return (
        float(data[0]["lat"]),
        float(data[0]["lon"]),
        data[0]["display_name"]
    )


def search_food_places(lat, lon, search_type):
    """Kajáldák keresése OpenStreetMapből."""

    radius = 5000

    if search_type == "mcdonalds":
        filter_query = """
        nwr["amenity"="fast_food"]["brand"="McDonald's"]
        """

    elif search_type == "kfc":
        filter_query = """
        nwr["amenity"="fast_food"]["brand"="KFC"]
        """

    elif search_type == "burgerking":
        filter_query = """
        nwr["amenity"="fast_food"]["brand"="Burger King"]
        """

    elif search_type == "pizza":
        filter_query = """
        nwr["amenity"~"restaurant|fast_food"]["cuisine"~"pizza",i]
        """

    elif search_type == "gyros":
        filter_query = """
        nwr["amenity"~"restaurant|fast_food"]["cuisine"~"kebab|greek",i]
        """

    elif search_type == "asian":
        filter_query = """
        nwr["amenity"~"restaurant|fast_food"]["cuisine"~"chinese|japanese|thai|asian|vietnamese",i]
        """

    else:
        filter_query = """
        nwr["amenity"~"restaurant|fast_food"]
        """

    query = f"""
    [out:json][timeout:20];

    (
        {filter_query}
        (around:{radius},{lat},{lon});
    );

    out center tags;
    """

    response = requests.post(
        OVERPASS_URL,
        data={
            "data": query
        },
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.json().get("elements", [])


def get_element_coordinates(element):
    """Node/way/relation koordinátáinak kezelése."""

    if element["type"] == "node":
        return (
            element.get("lat"),
            element.get("lon")
        )

    center = element.get("center", {})

    return (
        center.get("lat"),
        center.get("lon")
    )


def get_address(tags):
    """Megpróbál emberileg olvasható címet összerakni."""

    street = tags.get("addr:street")
    number = tags.get("addr:housenumber")
    city = tags.get("addr:city")

    parts = []

    if street:
        if number:
            parts.append(f"{street} {number}")
        else:
            parts.append(street)

    if city:
        parts.append(city)

    if parts:
        return ", ".join(parts)

    return "Nincs megadott cím"


def create_waze_url(lat, lon):
    """Waze navigációs link."""

    return (
        "https://www.waze.com/ul?"
        f"ll={lat},{lon}"
        "&navigate=yes"
    )


def create_osm_url(lat, lon):
    """OpenStreetMap link."""

    return (
        f"https://www.openstreetmap.org/"
        f"?mlat={lat}&mlon={lon}"
        f"#map=18/{lat}/{lon}"
    )


@app_commands.command(
    name="kajahely",
    description="Megkeresi a hozzád közeli kajáldákat."
)
@app_commands.describe(
    etterem="Milyen kajáldát keresel?",
    hely="Honnan keressek? Pl. Schönherz Kollégium"
)
@app_commands.choices(
    etterem=[
        app_commands.Choice(
            name="🍔 McDonald's",
            value="mcdonalds"
        ),
        app_commands.Choice(
            name="🍗 KFC",
            value="kfc"
        ),
        app_commands.Choice(
            name="👑 Burger King",
            value="burgerking"
        ),
        app_commands.Choice(
            name="🍕 Pizza",
            value="pizza"
        ),
        app_commands.Choice(
            name="🥙 Gyros / Kebab",
            value="gyros"
        ),
        app_commands.Choice(
            name="🍜 Ázsiai",
            value="asian"
        ),
        app_commands.Choice(
            name="🍽️ Bármi",
            value="anything"
        ),
    ]
)
async def foodplace(
    interaction: discord.Interaction,
    etterem: app_commands.Choice[str],
    hely: str
):
    await interaction.response.defer()

    try:
        coordinates = get_coordinates(hely)

        if coordinates is None:
            await interaction.followup.send(
                f"❌ Nem találtam ezt a helyet: **{hely}**"
            )
            return

        user_lat, user_lon, resolved_place = coordinates

        places = search_food_places(
            user_lat,
            user_lon,
            etterem.value
        )

        if not places:
            await interaction.followup.send(
                "😢 Nem találtam ilyen kajáldát 5 km-en belül."
            )
            return

        restaurants = []

        for element in places:
            lat, lon = get_element_coordinates(element)

            if lat is None or lon is None:
                continue

            tags = element.get("tags", {})

            name = tags.get("name")

            if not name:
                if etterem.value == "mcdonalds":
                    name = "McDonald's"
                elif etterem.value == "kfc":
                    name = "KFC"
                elif etterem.value == "burgerking":
                    name = "Burger King"
                else:
                    name = "Névtelen kajálda"

            distance = calculate_distance(
                user_lat,
                user_lon,
                lat,
                lon
            )

            restaurants.append({
                "name": name,
                "distance": distance,
                "lat": lat,
                "lon": lon,
                "tags": tags
            })

        restaurants.sort(
            key=lambda restaurant: restaurant["distance"]
        )

        embed = discord.Embed(
            title=f"🍔 {etterem.name}",
            description=(
                f"📍 Kiindulási hely:\n"
                f"**{resolved_place}**\n\n"
                f"🔎 5 km-es körzetben keresek."
            )
        )

        for index, restaurant in enumerate(
            restaurants[:5],
            start=1
        ):
            tags = restaurant["tags"]

            address = get_address(tags)

            opening_hours = tags.get("opening_hours")

            waze_url = create_waze_url(
                restaurant["lat"],
                restaurant["lon"]
            )

            osm_url = create_osm_url(
                restaurant["lat"],
                restaurant["lon"]
            )

            value = (
                f"📍 {address}\n"
                f"📏 **{restaurant['distance']:.2f} km**\n"
            )

            if opening_hours:
                value += (
                    f"🕒 `{opening_hours}`\n"
                )

            value += (
                f"🚗 [Waze]({waze_url})"
                f" • "
                f"🗺️ [OpenStreetMap]({osm_url})"
            )

            embed.add_field(
                name=(
                    f"{index}. "
                    f"{restaurant['name']}"
                ),
                value=value,
                inline=False
            )

        embed.set_footer(
            text=(
                "Adatok: © OpenStreetMap contributors • "
                "A távolság légvonalban értendő."
            )
        )

        await interaction.followup.send(
            embed=embed
        )

    except requests.Timeout:
        await interaction.followup.send(
            "⏱️ A térképszolgáltatás nem válaszolt időben."
        )

    except requests.RequestException as error:
        print(f"HTTP hiba: {error}")

        await interaction.followup.send(
            "❌ Hiba történt a térképadatok lekérése közben."
        )

    except Exception as error:
        print(f"Váratlan hiba: {error}")

        await interaction.followup.send(
            "❌ Valami váratlan hiba történt."
        )