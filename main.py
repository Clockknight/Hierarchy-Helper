import os
import memoryfuncs
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.presences = True
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
string''')
            case "!relate":
                if len(chunks) == 4:
                    server = message.channel.guild
                    role1 = parserole(message, chunks[1])
                    role2 = parserole(message, chunks[2])
                    relation = chunks[3]

                    await message.channel.send('Processing...')

                    #TODO save this information in a json
                    dict = {role1.id: {role2.id:relation}}
                    #go to json with guild id
                    #go to key with role1
                    #go to nested key with role2
                    #store role2

                    await message.channel.send('Saved!')

                    #TODO brainstorm role exceptions to consider

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
                    await message.author.add_roles(targetrole, reason="hierarchy helper getme command")

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


client.run(TOKEN)
