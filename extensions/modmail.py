############################################
# Discord Modmail Bot
# Author: @InvalidJoker
# Version: 1.0
# Diese Nachricht darf nicht entfernt werden!
############################################
import discord
from discord.ext import commands

import aiosqlite

from config import CATEGORY, GUILD

db: aiosqlite.Connection = None

class Modmail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @staticmethod
    async def has_ticket(user_id):
        cursor = await conn.execute("SELECT * FROM tickets WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return bool(row)
    
    @commands.Cog.listener()
    async def on_ready(self):
        global conn
        
        self.bot.add_view(CloseTicketView())

        conn = await aiosqlite.connect("tickets.db")
    
        await conn.execute(
            """CREATE TABLE IF NOT EXISTS tickets (
                channel_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL
            )"""
    )
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel) and not await self.has_ticket(message.author.id):
            guild = self.bot.get_guild(GUILD)
            category = guild.get_channel(CATEGORY)
            
            channel = await category.create_text_channel(f"ticket-{message.author.name}")

            await conn.execute("INSERT INTO tickets (user_id, channel_id) VALUES (?, ?)", (message.author.id, channel.id))
            await conn.commit()
            
            embed = discord.Embed(title="WILLKOMMEN IM TICKET-SUPPORT!",
                                description="""
    Ich habe deine Support-Anfrage erstellt und das Server-Team über dein Anliegen informiert.
                                """, color=discord.Color.green())
            embed.set_footer(text="Made by InvalidJoker")
            
            team_embed = discord.Embed(title="Neues Ticket!",
                                    description=f"Neues Ticket von: {message.author.mention}.", color=discord.Color.green())
            team_embed.set_footer(text="Made by InvalidJoker")
            
            await message.channel.send(embed=embed)
            await channel.send(embed=team_embed, view=CloseTicketView())
        
        elif isinstance(message.channel, discord.DMChannel) and await self.has_ticket(message.author.id):
            cursor = await conn.execute("SELECT channel_id FROM tickets WHERE user_id = ?", (message.author.id,))
            row = await cursor.fetchone()
            
            if row:
                channel_id = row[0]
                channel = self.bot.get_channel(channel_id)
                
                embed = discord.Embed(description=f"{message.content}", color=discord.Color.green())
                embed.set_author(name=message.author,
                                url=message.author.jump_url,
                                icon_url=message.author.avatar.url
                                )
                embed.set_footer(text="Made by InvalidJoker")

                await channel.send(embed=embed)
                await message.add_reaction("✅")
        
        elif message.channel.category_id == CATEGORY and not isinstance(message.channel, discord.DMChannel):
            cursor = await conn.execute("SELECT user_id FROM tickets WHERE channel_id = ?", (message.channel.id,))
            row = await cursor.fetchone()

            if row:
                user_id = row[0]
                user = self.bot.get_user(user_id)
                
                if user is None:
                    user = await self.bot.fetch_user(user_id)
                
                embed = discord.Embed(description=f"{message.content}", color=discord.Color.green())
                embed.set_author(name=message.author,
                                url=message.author.jump_url,
                                icon_url=message.author.avatar.url
                                )
                embed.set_footer(text="Made by InvalidJoker")

                await user.send(embed=embed)
                await message.add_reaction("✅")
        
        await self.bot.process_commands(message)


def setup(bot):
    bot.add_cog(Modmail(bot))
    
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        cursor = await conn.execute("SELECT user_id FROM tickets WHERE channel_id = ?", (interaction.channel.id,))
        user_id = await cursor.fetchone()
        user_id = user_id[0]
        
        await conn.execute("DELETE FROM tickets WHERE channel_id = ?", (interaction.channel.id,))
        await conn.commit() 
        
        user = interaction.client.get_user(user_id)
        if user is None:
            user = await interaction.client.fetch_user(user_id)

        await interaction.response.send_message("Dein Ticket wird geschlossen...")
        await user.send("Dein Ticket wurde geschlossen.")
        await interaction.message.channel.delete()
