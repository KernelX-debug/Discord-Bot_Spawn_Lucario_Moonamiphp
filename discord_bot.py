import os
import html
import re
import requests
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


def limpiar_html(texto):
    texto = html.unescape(str(texto))
    return re.sub(r"<[^>]+>", "", texto).strip()


def extraer_coords(texto):
    match = re.search(r'data-clipboard-text="([^"]+)"', str(texto))
    return match.group(1) if match else ""


def buscar_pokemon_iv100(nombre_busqueda, limite=5):
    url = "https://moonani.com/PokeList/ajax.php?page=pokemon&action=load"

    payload = {
        "iv": 100,
        "pvp": 0,
        "pokemons": "",
        "start": 0,
        "length": 250,
        "draw": 1,
    }

    headers = {
        "Referer": "https://moonani.com/PokeList/index.php",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0",
    }

    r = requests.post(
        url,
        data=payload,
        headers=headers,
        timeout=20,
    )

    r.raise_for_status()

    data = r.json().get("data", [])

    resultados = []

    for pokemon in data:
        nombre = limpiar_html(pokemon["Name"])

        if nombre_busqueda.lower() not in nombre.lower():
            continue

        resultados.append(
            {
                "nombre": nombre,
                "numero": pokemon["Number"],
                "coords": extraer_coords(pokemon["Coords"]),
                "cp": pokemon["CP"],
                "nivel": pokemon["Level"],
                "inicio": pokemon["Start Time"],
                "fin": pokemon["End Time"],
            }
        )

        if len(resultados) >= limite:
            break

    return resultados


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync(guild=GUILD)
        print(f"Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(e)

    print(f"Conectado como {bot.user}")


GUILD = discord.Object(id=GUILD_ID)

@bot.tree.command(
    name="pokemon",
    description="Buscar Pokemon IV100",
    guild=GUILD
)

@app_commands.describe(nombre="Nombre del pokemon")
async def pokemon(
    interaction: discord.Interaction,
    nombre: str
):
    await interaction.response.defer()

    try:
        resultados = buscar_pokemon_iv100(nombre)

        if not resultados:
            await interaction.followup.send(
                "No encontré resultados."
            )
            return

        mensajes = []

        for p in resultados:
            mensajes.append(
                f"🎯 **{p['nombre']}** #{p['numero']}\n"
                f"📍 {p['coords']}\n"
                f"⚡ CP {p['cp']} | Nivel {p['nivel']}\n"
                f"⏱️ {p['inicio']} → {p['fin']}\n"
                f"🗺️ https://maps.google.com/?q={p['coords']}"
            )

        await interaction.followup.send(
            "\n\n".join(mensajes)
        )

    except Exception as e:
        await interaction.followup.send(
            f"Error: {e}"
        )


bot.run(TOKEN)
