import os
from dotenv import load_dotenv
import json
import disnake
from disnake.ext import commands

# TODO operate under assumption only one relation exists (heirarchy) ignore others
# TODO refactor code so this is consistent (below can be reversed, just should be consistent)
# In general, r1 {r2:1} means r1 is the child of r2
#          ...r1 {r2:2} means r1 is the parent of r2

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = disnake.Intents(message_content=True, members=True, guilds=True)
bot = commands.Bot(intents=intents, command_prefix='$', sync_commands_debug=True, test_guilds=[996239355704258590])


# bot = commands.Bot(intents=intents, command_prefix='$', test_guilds=[996239355704258590])


@bot.slash_command(description="This will define the relation for the server, and immediately enforce it.")
async def makerelation(inter, parent: str, child: str,
                       relationtype: str = commands.Param(choices=["Heirarchy", "Matching", "Highlander"])):
    print(relationtype)


@bot.slash_command(description="A user will be given parent if they ever get child. Also, ")
async def test(inter, parent: str, child: str):
    await relationLogic(inter, child, parent, 1)


@bot.event
async def on_member_update(before, after):
    newRole = None
    if len(before.roles) < len(after.roles):
        newRole = next(role for role in after.roles if role not in before.roles)
    elif len(before.roles) > len(after.roles):
        newRole = next(role for role in before.roles if role not in after.roles)
    if newRole is not None:
        await updateRoles(newRole, after)


async def relationLogic(inter, role1: disnake.Role, role2: disnake.Role, relationclass: int):
    """Whenever one of the slash commands for defining roles is called, this function processes the actual logic
    of storing all the information, since each one is essentially the same process.
    """
    print(inter)
    # TODO Check if user has correct permissions to do this
    # Probably looking for admin perms + ability to assign/remove roles
    # TODO refactor relationLogic to deal with relations being two way
    # TODO refactor variableCheck...
    # TODO refactor relationDefine...
    role1, role2, invalidrolebool = variableCheck(inter, role1, role2)
    if invalidrolebool:
        await inter.response.send_message('Sorry! One of the roles input was invalid.')
        return
    j = relationDefine(inter.channel.guild.id, role1, role2, relationclass)
    if not j:
        await inter.response.send_message('Sorry! The relation was not able to be saved.')

    status = 'Saved! Now when people get the {} role, they will automatically get the {} role.'.format(role1.mention,
                                                                                                       role2.mention)
    match relationclass:
        case 1:
            await updateRoles(role2, jsoncontents=j)

    await inter.response.send_message(status)


def variableCheck(inter, r1, r2):
    """Given the context of a command, and the raw string of two roles':
    Return the role objects in the server the command was sent from, using guild.get_role() from Disnake
    And return true if either is None
    """
    r1 = findRole(inter, r1)
    r2 = findRole(inter, r2)
    invalidrolebool = (r1 is None or r2 is None)
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
    # TODO implement checking for paradoxes
    print(relation)


def relationDefine(guildid, role1, role2, relationid):
    """
    Given two roles, the ID of the relation to be established and the guild they're in:
    Define a dict object describing the relation, run it through checkRelationParadox()

    If checkRelationParadox() returns true, immediately return True
    Else, updateJson() with the new relation, then updateRoles() on the server, then return False.
    """
    relation = {str(role1.id): {str(role2.id): relationid}}
    if checkRelationParadox(relation):
        return False
    jsoncontents = updateJson(guildid, relation)
    return jsoncontents


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
    # If the key from new relation doesn't already exist, update the whole json instead
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
        if not os.path.exists('./guilds'):
            os.makedirs('./guilds')
        f = open(jsondir, 'w+')
        f.write('{\n}')
        f.close()
    f = open(jsondir, 'r')
    jsoncontents = json.load(f)
    f.close()

    return jsoncontents, jsondir


async def updateRoles(role, member=None, jsoncontents=None):
    """Given a role, update it to follow all relations stored in the guild specific JSON
    member, is member object to update.
    If not provided, then this function will update the role for all users on the server.
    jsoncontents, must be a dict of the guild-specific json. If not provided, then readJson() is called.
    """

    key = str(role.id)
    guild = role.guild
    addroles = []
    removeroles = []
    if member is None:
        member = guild.members
    else:
        member = [member]

    if jsoncontents is None:
        jsoncontents = readJson(guild.id)[0]

    if key not in list(jsoncontents.keys()):
        return

    for targetmember in member:
        rolepresent = True if role in targetmember.roles else False
        for roleid in jsoncontents[key]:
            targetrole = guild.get_role(int(roleid))
            match jsoncontents[key][roleid], rolepresent:
                # Child of heirarchy
                case 1, True:
                    addroles.append(targetrole)
                # Parent of Heirarchy
                case 2, False:
                    removeroles.append(targetrole)

        print('\n\nChanging roles')
        if addroles:
            print(addroles)
            for role in addroles:
                await targetmember.add_roles(role)
        if removeroles:
            print(removeroles)
            for role in removeroles:
                await targetmember.remove_roles(role)

    # TODO make all roles get added/removed at once
    # Get array of all members with role

    # get role1 = get role2 //hierarchize
    # rm role1 = dont care

    # get role1 = rm role2 // same either direction
    # rm role1 = get role2

    # Paired
    # rm role1 = rm role2 // Similar to hierarchize ?
    # get role1 = get role2
    # also, paired/symmetrical versions of above

    # TODO make a two part function that removes a specific role-to-role function
    # put considerations for symmetrical relations

    # TODO make a function that reports all relations, a simple list is fine


bot.run(TOKEN)
