from discord.ext import commands
from discord import app_commands, Interaction
from collections import deque
import discord

SONG_QUEUES = {}

class Musica(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="play", description="Toca uma música ou adiciona à fila.")
    @app_commands.describe(song_query="Nome da música ou link")
    async def play(self, interaction: Interaction, song_query: str):
        await interaction.response.defer()

        voice_channel = interaction.user.voice.channel
        if voice_channel is None:
            await interaction.followup.send("Você precisa estar em um canal de voz.")
            return

        voice_client = interaction.guild.voice_client
        if voice_client is None:
            voice_client = await voice_channel.connect()
        elif voice_channel != voice_client.channel:
            await voice_client.move_to(voice_channel)

        ydl_options = {
            "format": "bestaudio[abr<=96]/bestaudio",
            "noplaylist": True,
            "youtube_include_dash_manifest": False,
            "youtube_include_hls_manifest": False,
            "default_search": "ytsearch"
        }

        query = "ytsearch1: " + song_query
        results = await search_ytdlp_async(query, ydl_options)
        tracks = results.get("entries", [])
        if not tracks:
            await interaction.followup.send("Nenhum resultado encontrado.")
            return

        first_track = tracks[0]
        audio_url = first_track["url"]
        title = first_track.get("title", "Sem título")

        guild_id = str(interaction.guild_id)
        if SONG_QUEUES.get(guild_id) is None:
            SONG_QUEUES[guild_id] = deque()
        SONG_QUEUES[guild_id].append((audio_url, title))

        if voice_client.is_playing() or voice_client.is_paused():
            await interaction.followup.send(f"🎵 Adicionado à fila: **{title}**")
        else:
            await interaction.followup.send(f"▶️ Tocando agora: **{title}**")
            await self.play_next_song(voice_client, guild_id, interaction.channel)

    @app_commands.command(name="pause", description="Pausa a música.")
    async def pause(self, interaction: Interaction):
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.response.send_message("Não estou em um canal de voz.")
            return
        if not vc.is_playing():
            await interaction.response.send_message("Nada está tocando.")
            return
        vc.pause()
        await interaction.response.send_message("⏸ Música pausada.")

    @app_commands.command(name="resume", description="Retoma a música.")
    async def resume(self, interaction: Interaction):
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.response.send_message("Não estou em um canal de voz.")
            return
        if not vc.is_paused():
            await interaction.response.send_message("Não estou pausado.")
            return
        vc.resume()
        await interaction.response.send_message("▶️ Música retomada.")

    @app_commands.command(name="stop", description="Para a música e limpa a fila.")
    async def stop(self, interaction: Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            await interaction.response.send_message("Não estou conectado.")
            return

        guild_id = str(interaction.guild_id)
        SONG_QUEUES[guild_id].clear()
        if vc.is_playing() or vc.is_paused():
            vc.stop()
        await vc.disconnect()
        await interaction.response.send_message("⏹ Parado e desconectado.")

    @app_commands.command(name="skip", description="Pula a música atual.")
    async def skip(self, interaction: Interaction):
        vc = interaction.guild.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            await interaction.response.send_message("⏭ Música pulada.")
        else:
            await interaction.response.send_message("Nada tocando.")

    async def play_next_song(self, voice_client, guild_id, channel):
        if SONG_QUEUES[guild_id]:
            audio_url, title = SONG_QUEUES[guild_id].popleft()

            ffmpeg_options = {
                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                "options": "-vn -c:a libopus -b:a 96k"
            }

            source = discord.FFmpegOpusAudio(audio_url, **ffmpeg_options, executable="bin\\ffmpeg\\ffmpeg.exe")

            def after_play(error):
                if error:
                    print(f"Erro ao tocar {title}: {error}")
                self.bot.loop.create_task(self.play_next_song(voice_client, guild_id, channel))

            voice_client.play(source, after=after_play)
            await channel.send(f"▶️ Tocando agora: **{title}**")
        else:
            await voice_client.disconnect()
            SONG_QUEUES[guild_id] = deque()

async def setup(bot):
    await bot.add_cog(Musica(bot))
