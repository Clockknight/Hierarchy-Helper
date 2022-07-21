import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
# Might need presences later
# intents = discord.Intents(guilds=True, members=True, presences=True)
# for now this is the minimum required intents
intents = discord.Intents(guilds=True, members=True)
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content
    if msg.startswith('!'):
        chunks = msg.split(' ')
        match chunks[0].lower():
            case "!help":
                await message.channel.send('''Test
string
lets find out''')
            case "!relate":
                if len(chunks) != 4:
                    # TODO Bot takes commands with several arguments, including:
                    """
                    role1
                    role2
                    Relation between roles
                    """
                    return
            case _:
                await message.channel.send('Invalid command, please use \"!Help\" for a list of commands.')


@client.event
async def on_member_update(before, after):
    # TODO Bot notices when someone has a role added or removed
    print(after.roles)
    if len(before.roles) < len(after.roles):
        newRole = next(role for role in after.roles if role not in before.roles)
        if newRole.name == "Respected":
            print('ping')
            # This uses the name, but you could always use newRole.id == Roleid here
            # Now, simply put the code you want to run whenever someone gets the "Respected" role here


# TODO Define role relations
# TODO Store role relations, per server in some info file somewhere, using pandas library

client.run(TOKEN)
