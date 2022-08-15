import json
import os
import discord
from discord.ext import commands as cmd
import disnake
from disnake.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.presences = True
client = cmd.Bot(command_prefix='$', intents=intents, help_command=None)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        print(message.guild.id)
        return

    msg = message.content
    if msg.startswith('!'):
        chunks = msg.split(' ')
        match chunks[0].lower():
            case "!help":
                # TODO write actual help
                await message.channel.send('''Teststring''')
            case "!relate":
                if len(chunks) == 4:
                    server = str(message.channel.guild)
                    role1 = parserole(message, chunks[1])
                    role2 = parserole(message, chunks[2])
                    relation = chunks[3]

                    await message.channel.send('Processing...')

                    # TODO save this information in a json
                    dict = {role1.id: {role2.id: relation}}
                    writejson(server, dict)
                    # go to key with role1
                    # go to nested key with role2
                    # store role2

                    await message.channel.send('Saved!')

                    # TODO brainstorm role exceptions to consider
                    # if role1, give role2
                    # if role1, remove role2
                    # role2 = role1

                    return
                else:
                    await message.channel.send('Incorrect number of arguments')

            case "!giveme":
                msgchan = message.channel
                words = message.content.split(" ")

                if (type(msgchan) == discord.channel.DMChannel):
                    await msgchan.send('Error: Can\'t assign roles in direct messages')
                    return
                if len(words) < 2:
                    await msgchan.send('Error: More arguments required for !giveme command')
                    return
                await msgchan.send('Input recieved, printing results in console')

                id = words[1]
                targetrole = parserole(message, id)

                if targetrole == "":
                    await message.channel.send('Error: No such role found.')
                    return
                else:
                    await message.author.add_roles(targetrole, reason="hierarchy helper giveme command")

            case _:
                await message.channel.send('Invalid command, please use \"!Help\" for a list of commands.')


@client.event
async def on_member_update(before, after):
    # TODO Bot notices when someone has a role added or removed
    print(before)
    print(after.roles)
    if len(before.roles) < len(after.roles):
        newRole = next(role for role in after.roles if role not in before.roles)
        if newRole.name == "Respected":
            print('ping')


@client.command(name="ping")
async def ping(ctx):
    print('p')


'''
@bot.command()
async def test(ctx):
    print('test')
    pass

@bot.command()
async def t(ctx):
    print(ctx.message)
    await ctx.send('t')
    pass
'''


# TODO Define role relations

def parserole(message, roleid):
    """Given specific message and id number of a role, find the role on the server with the same id then return it.
    Else, return an empty string."""
    # TODO send a message if roleid isnt an integer
    roleid = roleid[3:-1]
    roleid = int(roleid)
    for role in message.channel.guild.roles:
        if role.id == roleid:
            return role

    return ""


def writejson(gid, dict):
    dir = './guilds/' + gid + '.json'
    f = open(dir, 'r') if os.path.exists(dir) else open(dir, 'w+')
    json.load(f)


client.run(TOKEN)
