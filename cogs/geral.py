import discord, random, asyncio, aiohttp
from discord.ext import commands
from discord import Embed
from asteval import Interpreter

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

class Geral(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="📐 Calcula uma expressão matemática. Ex: .calc 2 + 2")
    async def calc(self, ctx, *, expr):
        aeval = Interpreter()
        try:
            result = aeval(expr)
            if result is None:
                await ctx.reply("Expressão inválida ou resultado indefinido.")
            else:
                await ctx.send(f"`{expr}` = `{result}`")
        except Exception as e:
            await ctx.reply(f"Erro ao calcular: {str(e)}")

    @commands.command(help="👋 Diz oi para o bot.")
    async def oi(self, ctx):
        await ctx.reply(f"Oi, {ctx.author.name}! Tudo bem?")

    @commands.command(help="🎲 Gira um dado, informe também o tipo de dado. Ex: .dado 20")
    async def dado(self, ctx, tipo: int):
        if tipo < 2 or tipo > 100 or not isinstance(tipo, int):
            return await ctx.reply("O tipo de dado deve ser um número inteiro maior que 2 e menor que 100.")
        await ctx.reply("🎲 Rolando o dado...")
        await asyncio.sleep(3)
        resultado = random.randint(1, tipo)
        await ctx.reply(f"🎲 Você rolou um dado de {tipo} lados e saiu: **{resultado}**")
        

    @commands.command(help="📜 Mostra a lista de comandos disponíveis.")
    async def help(self, ctx):
        embed = discord.Embed(
            title="📘 Lista de comandos disponíveis",
            description="Veja abaixo os comandos disponíveis para você usar:",
            color=discord.Color.blue()
        )
        # Ordena os comandos pelo nome
        comandos_ordenados = sorted(self.bot.commands, key=lambda c: c.name)
        for command in comandos_ordenados:
            if not command.hidden:
                embed.add_field(
                    name=f"`.{command.name}`",
                    value=command.help or "Sem descrição",
                    inline=False
                )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Geral(bot))
    bot.load_extension("cogs.geral")
