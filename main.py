import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = 'YOUR_DISCORD_BOT_TOKEN'

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="/", intents=intents)
bot.remove_command("help")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
    # Load all cogs from the cmds folder
    for filename in os.listdir("./cmd"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cmds.{filename[:-3]}")
    
    # Sync the slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} Slash commands")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    bot.run(TOKEN)
