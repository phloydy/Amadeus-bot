import os
from discord.ext import commands
from dotenv import load_dotenv
import discord

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

# bot.spotify_credentials = {
#     "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
#     "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET")
# }

# bot.lavalink_nodes = [
#     {
#         "host": "lava-v4.ajieblogs.eu.org",
#         "port": 443,
#         "password": "https://dsc.gg/ajidevserver",
#         "identifier": "main",
#         "secure": True
#     }
# ]

EXTENSIONS = [
    "cogs.geral",
    "cogs.moderacao",
    "cogs.eventos",
    "cogs.musica",
    "cogs.waifu",
    "cogs.anichar",
    "cogs.ai",
    "cogs.animus",
]

# bot.load_extension("jishaku")  # Uncomment if you want to use jishaku for debugging
import asyncio

async def run_bot():
    for ext in EXTENSIONS:
        try:
            await bot.load_extension(ext)
            print(f"✅ {ext} carregado")
        except Exception as e:
            print(f"❌ Erro ao carregar {ext}: {e}")
    await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(run_bot())
