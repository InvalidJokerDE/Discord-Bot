############################################
# Discord Radio Bot
# Author: @InvalidJoker
# Version: 1.0
# Diese Nachricht darf nicht entfernt werden!
############################################
import discord
from discord.ext import commands, tasks

import asyncio

from config import CHANNEL


class Radio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(CHANNEL)

        await channel.connect()
        channel.guild.voice_client.play(discord.FFmpegPCMAudio("https://streams.ilovemusic.de/iloveradio16.mp3"))
        self.check_music.start()
        self.auto_restart.start()
        
    @tasks.loop(seconds=60)
    async def check_music(self):
        channel = self.bot.get_channel(CHANNEL)
        
        if channel.guild.voice_client is None:
            await channel.connect()
            channel.guild.voice_client.play(discord.FFmpegPCMAudio("https://streams.ilovemusic.de/iloveradio16.mp3"))
            
        if channel.guild.voice_client.is_playing() == False:
            channel.guild.voice_client.play(discord.FFmpegPCMAudio("https://streams.ilovemusic.de/iloveradio16.mp3"))

    @tasks.loop(hours=24)
    async def auto_restart(self):
        channel = self.bot.get_channel(CHANNEL)
        
        if channel.guild.voice_client:
            if self.check_music.is_running():
                self.check_music.stop()
            
            await channel.guild.voice_client.disconnect()
            await asyncio.sleep(5)
            await channel.connect()
            channel.guild.voice_client.play(discord.FFmpegPCMAudio("https://streams.ilovemusic.de/iloveradio16.mp3"))
            if self.check_music.is_running() == False:
                self.check_music.start()


def setup(bot):
    bot.add_cog(Radio(bot))