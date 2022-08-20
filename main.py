import os
from dotenv import load_dotenv
import json
import disnake
from disnake.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = disnake.Intents(message_content=True, members=True, guilds=True)
# intents.
bot = commands.Bot(intents=intents, command_prefix='$', sync_commands_debug=True, test_guilds=[996239355704258590])


# bot = commands.Bot(intents=intents, command_prefix='$', test_guilds=[996239355704258590])


@bot.slash_command(description="A user will be given role1 if they ever get role2.")
async def hierarchize(inter, role1: str, role2: str):
    # TODO Check if user has correct permissions to do this
    # Probably looking for admin perms + ability to assign/remove roles
    role1, role2, invalidrolebool = variableCheck(inter, role1, role2)
    if invalidrolebool:
        await inter.response.send_message('no')
    else:
        status = 'Saved! Now people will be given {} if they get {}'.format(role1.mention, role2.mention)
        await inter.response.send_message(status)
        relationDefine(inter.channel.guild.id, role1, role2, 1)


@bot.slash_command(description="A user will be given role1 if they get role2, or vice-versa.")
async def match(inter, role1: str, role2: str):
    role1, role2, invalidrolebool = variableCheck(inter, role1, role2)
    if invalidrolebool:
        await inter.response.send_message('no')
    else:
        await inter.response.send_message('k')


@bot.slash_command(description="Someone can ONLY have role1 or role2.")
async def noncompatible(inter, role1: str, role2: str):
    role1, role2, invalidrolebool = variableCheck(inter, role1, role2)
    if invalidrolebool:
        await inter.response.send_message('no')
    else:
        await inter.response.send_message('k')


@bot.event
async def on_member_update(before, after):
    # Make this update roles according to roles on readJson
    if len(before.roles) < len(after.roles):
        newRole = next(role for role in after.roles if role not in before.roles)
        if newRole.name == "Respected":
            print('ping')


def variableCheck(inter, r1, r2):
    """Given the context of a command, and the raw string of two roles':
    """
    r1 = findRole(inter, r1)
    r2 = findRole(inter, r2)
    invalidrolebool = r1 == '' and r2 == ''
    return r1, r2, invalidrolebool


def findRole(inter, roleid):
    """Given command context and the raw value of a role, return the value given if it matches a role on the server.
    Else, return an empty string."""
    roleid = roleid[3:-1]
    roleid = int(roleid)
    return inter.guild.get_role(roleid)


def checkRelationParadox(relation):
    """
    Return true if a paradox is detected.
    Else, return false.
    """
    print(relation)


def relationDefine(guildid, role1, role2, relationid):
    relation = {str(role1.id): {str(role2.id): relationid}}
    if not checkRelationParadox(relation):
        jsoncontents = updateJson(guildid, relation)
    else:
        return True


def updateJson(gid, newrelation):
    """Given the id of a guild and a dictionary object that represents a new relation between two roles:
    Ensure no paradox is created, with checkRelationParadox(),
    then update the json file with the dictionary object.

    Return the updated contents of the json file"""

    # Use readJson variables later to write to Json

    jsoncontents, jsondir = readJson(gid)

    # Get the key from the new relation and the stored relations
    key = list(newrelation.keys())[0]
    keys = list(jsoncontents.keys())

    # Check if role has already been interacted with role
    if key in keys:
        jsoncontents[key].update(newrelation[key])
    else:
        jsoncontents.update(newrelation)

    f = open(jsondir, 'w')
    f.write(json.dumps(jsoncontents, indent=4))
    f.close()

    return jsoncontents


def readJson(gid):
    """Given the id of a guild, read the contents of the server-specific json.
    Create an empty json, if it doesn't already exist so the contents are {}.

    Return the directory of the json file,
    and return the contents of the json as a dict object.
    """
    jsondir = './guilds/{}.json'.format(gid)
    if not os.path.exists(jsondir):
        os.makedirs('./guilds')
        f = open(jsondir, 'w+')
        f.write('{\n}')
        f.close()
    f = open(jsondir, 'r')
    jsoncontents = json.load(f)
    f.close()

    return jsoncontents, jsondir


def updateRoles(role, jsoncontents=None):
    if jsoncontents == None:
        jsoncontents = readJson(role.guild)


bot.run(TOKEN)
