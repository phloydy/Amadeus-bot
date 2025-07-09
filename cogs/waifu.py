import aiohttp, asyncio
from discord.ext import commands
import discord

class Gacha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.harems = {}  # {user_id: [characters...]}

    @commands.command(help="💘 10 waifus aleatórias. Reaja com 💖 para pegar!")
    async def waifu(self, ctx):
        quantidade = 10
        favoritos_min = 200
        waifus = []

        await ctx.send("🔎 Procurando waifus, aguarde...")

        async def fetch_waifu(session):
            for _ in range(20):  # tenta até 20 vezes por tarefa
                async with session.get("https://api.jikan.moe/v4/random/characters") as r:
                    data = await r.json()
                    c = data.get("data")
                    if (
                        c
                        and c.get("images")
                        and c["images"]["jpg"]["image_url"]
                        and not c["images"]["jpg"]["image_url"].endswith("questionmark_23.gif")
                        and c.get("favorites", 0) >= favoritos_min
                    ):
                        return {
                            "name": c["name"],
                            "image": c["images"]["jpg"]["image_url"],
                            "mal_id": c["mal_id"]
                        }
            return None

        async with aiohttp.ClientSession() as session:
            tasks = [fetch_waifu(session) for _ in range(quantidade * 2)]  # cria mais tarefas para garantir
            results = await asyncio.gather(*tasks)
            waifus = [w for w in results if w][:quantidade]

        if len(waifus) < quantidade:
            await ctx.send(f"⚠️ Só consegui encontrar {len(waifus)} waifus. Tente novamente mais tarde!")
        else:
            await ctx.send("✅ Waifus encontradas!")

        for waifu in waifus:
            serie = "Desconhecido"
            # Tenta buscar o título do anime da waifu
            try:
                async with aiohttp.ClientSession() as session2:
                    url_anime = f"https://api.jikan.moe/v4/characters/{waifu.get('mal_id', 0)}/anime"
                    url_manga = f"https://api.jikan.moe/v4/characters/{waifu.get('mal_id', 0)}/manga"
                    async with session2.get(url_anime) as r2:
                        data2 = await r2.json()
                        anime_list = data2.get("data", [])
                        if anime_list:
                            serie = anime_list[0].get("anime", {}).get("title", "Desconhecido")
                        else:
                            async with session2.get(url_manga) as r3:
                                data3 = await r3.json()
                                manga_list = data3.get("data", [])
                                if manga_list:
                                    serie = manga_list[0].get("manga", {}).get("title", "Desconhecido")
            except Exception:
                pass

            embed = discord.Embed(
                title=f"{waifu['name']}",
                description=f"**{serie}**\nReaja com 💖 para pegar!",
                color=discord.Color.purple()
            )
            embed.set_image(url=waifu["image"])
            msg = await ctx.send(embed=embed)
            await msg.add_reaction("💖")

            async def handle_heart(msg, waifu):
                def check(reaction, user):
                    return (
                        str(reaction.emoji) == "💖"
                        and reaction.message.id == msg.id
                        and not user.bot
                    )
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                    await msg.remove_reaction(reaction, user)
                    self.harems.setdefault(user.id, []).append(waifu)
                    await ctx.send(f"💖 {user.mention} pegou **{waifu['name']}**!")
                except asyncio.TimeoutError:
                    pass

            asyncio.create_task(handle_heart(msg, waifu))

    @commands.command(help="📒 Mostra seu conjunto de waifus.")
    async def waifulist(self, ctx):
        arr = self.harems.get(ctx.author.id, [])
        if not arr:
            return await ctx.send("Você não tem nenhuma waifu ainda.")
        embed = discord.Embed(
            title=f"Lista de waifus de {ctx.author.display_name}",
            description="\n".join(f"• **{c['name']}**" for c in arr),
            color=discord.Color.magenta()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Gacha(bot))
# filepath: cogs/waifu.py