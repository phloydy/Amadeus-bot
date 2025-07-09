from discord.ext import commands
import discord
import math

class Eventos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Bot {self.bot.user.name} inicializado com sucesso!")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        canal = guild.system_channel
        if canal is None:
            for c in guild.text_channels:
                if "vindo" in c.name.lower():
                    canal = c
                    break
        if canal:
            await canal.send(f"🎉 Bem-vindo(a) {member.mention} ao servidor {guild.name}!")

    @commands.Cog.listener()
    async def on_connect(self):
        await self.bot.change_presence(activity=discord.Game(name=".help"))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("🚫 Você não tem permissão para usar este comando.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⚠️ Argumento obrigatório ausente.")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("❓ Comando não encontrado. Use `.help` para ajuda.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Cooldown: {math.ceil(error.retry_after)} segundos.")
        else:
            await ctx.send(f"❌ Ocorreu um erro: {error}")

async def setup(bot):
    await bot.add_cog(Eventos(bot))