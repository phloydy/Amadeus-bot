from discord.ext import commands

class Moderacao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="🧹 Limpa uma quantidade específica de mensagens ou todas. Ex: .clear 10 ou .clear all")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, qtd):
        if isinstance(qtd, str) and (qtd.lower() in ["all", "tudo", "."]):
            qtd = 100000000
            await ctx.channel.purge(limit=qtd)
            await ctx.send("🧹 Apaguei todas mensagens deste canal.", delete_after=5)
        else:
            try:
                qtd_int = int(qtd)
                if qtd_int > 1000 or qtd_int < 1:
                    await ctx.reply("Por favor, insira um número entre 1 e 1000.")
                    return
                deleted = await ctx.channel.purge(limit=qtd_int + 1)
                await ctx.send(f"🧹 Apaguei {len(deleted)-1} mensagens.", delete_after=5)
            except ValueError:
                await ctx.reply("Digite um número válido ou 'all', 'tudo', '.'.")

async def setup(bot):
    await bot.add_cog(Moderacao(bot))