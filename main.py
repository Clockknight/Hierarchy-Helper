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
    role1, role2, invalidrolebool = variableCheck(inter, role1, role2)
    if invalidrolebool:
        await inter.response.send_message('no')
    else:
        tstring = '{} {}'.format(role1.id, role2.id)
        await inter.response.send_message(tstring)
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
    if len(before.roles) < len(after.roles):
        newRole = next(role for role in after.roles if role not in before.roles)
        if newRole.name == "Respected":
            print('ping')


def variableCheck(inter, r1, r2):
    """Given the context of a command, and the raw string of two roles':
    """
    r1 = roleCheck(inter, r1)
    r2 = roleCheck(inter, r2)
    invalidrolebool = r1 == '' and r2 == ''
    return r1, r2, invalidrolebool


def roleCheck(inter, roleid):
    """Given command context and the raw value of a role, return the value given if it matches a role on the server.
    Else, return an empty string."""
    roleid = roleid[3:-1]
    roleid = int(roleid)
    for role in inter.guild.roles:
        if role.id == roleid:
            return role
    return ""


def checkRelationParadox(inter):
    """
    Return true if a paradox is detected.
    Else, return false.
    """
    print(inter)


def relationDefine(guildid, role1, role2, relationid):
    relation = {role1.id: {role2.id: relationid}}
    print(relation)
    writeJson(guildid, relation)


def writeJson(gid, newrelation):
    """Given the id of a guild and a dictionary object that represents a new relation between two roles:
    Ensure no paradox is created, with checkRelationParadox(),
    then update the json file with the dictionary object."""
    jsonDir = './guilds/{}.json'.format(gid)
    if not os.path.exists(jsonDir):
        os.makedirs('./guilds')
        f = open(jsonDir, 'w+')
        f.write('{\n}')
        f.close()
    f = open(jsonDir, 'r+')
    thing = json.load(f)
    # TODO finish writeJson


bot.run(TOKEN)
