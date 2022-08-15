import os
from dotenv import load_dotenv

import disnake
from disnake.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = disnake.Intents.default()
intents.guilds = True
intents.members = True
intents.presences = True
intents.message_content = True
bot = commands.Bot(intents=intents, command_prefix='$', sync_commands_debug=True)

# test_guilds=[996239355704258590]

@bot.slash_command(description="Responds with 'World'")
async def hello(inter):
    await inter.response.send_message("World")

bot.run(TOKEN)
