import discord
import os
import config

bot = discord.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('Online')
    print(f'{bot.user} is online!')


if __name__ == "__main__":
    for filename in os.listdir("extensions"):
        if filename.endswith(".py"):
            try:
                bot.load_extension(f"extensions.{filename[:-3]}")
                print(f"{filename[:-3]} ✅")
                
            except Exception as e:
                print(f"{filename[:-3]} ❌")
                raise e
            
    bot.run(config.TOKEN)
