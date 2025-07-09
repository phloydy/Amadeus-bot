import aiohttp, asyncio
from discord.ext import commands
import discord
import unicodedata
import string

class AniChar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="🎮 Tente adivinhar o personagem de anime pela imagem!")
    async def anichar(self, ctx):
        favoritos_min = 200
        max_tentativas = 50 

        await ctx.send("🔎 Procurando personagem, aguarde...")

        async def fetch_char(session):
            for _ in range(10):  # tenta até 10 vezes por tarefa
                async with session.get("https://api.jikan.moe/v4/random/characters") as resp:
                    data = await resp.json()
                    char = data["data"]
                    nome = char["name"]
                    imagem = char["images"]["jpg"]["image_url"]
                    favoritos = char.get("favorites", 0)
                    if (
                        imagem
                        and not imagem.endswith("questionmark_23.gif")
                        and favoritos >= favoritos_min
                    ):
                        return char
            return None

        async with aiohttp.ClientSession() as session:
            tasks = [fetch_char(session) for _ in range(5)]  # 5 buscas em paralelo
            results = await asyncio.gather(*tasks)
            char = next((c for c in results if c), None)

        if not char:
            await ctx.send("Não consegui encontrar um personagem popular. Tente novamente!")
            return

        nomes_possiveis = [n.strip().lower() for n in char["name"].replace(",", "/").replace(";", "/").split("/") if n.strip()]
        imagem = char["images"]["jpg"]["image_url"]

        embed = discord.Embed(
            title="Quem é esse personagem?",
            description="Responda neste chat! Você tem 30 segundos.",
            color=discord.Color.orange()
        )
        embed.set_image(url=imagem)
        await ctx.send(embed=embed)

        def check(m):
            return m.channel == ctx.channel and not m.author.bot

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Tempo esgotado! Era **{char['name']}**.")
            return

        def normalize(text):
            text = unicodedata.normalize('NFD', text)
            text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
            text = text.lower()
            text = ''.join(c for c in text if c not in string.punctuation)
            return text.strip()

        resposta = normalize(msg.content)
        nomes_norm = []
        for nome in nomes_possiveis:
            nomes_norm.extend(normalize(part) for part in nome.split())
        # Agora nomes_norm tem todos os pedaços dos nomes possíveis

        if any(n in resposta for n in nomes_norm if n):
            await ctx.send(f"🎉 Parabéns, {msg.author.mention}! Você acertou: **{char['name']}**")
        else:
            await ctx.send(f"❌ Errou! A resposta era **{char['name']}**.")

async def setup(bot):
    await bot.add_cog(AniChar(bot))
