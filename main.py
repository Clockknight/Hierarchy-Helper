import os
from dotenv import load_dotenv
import json
import disnake
from disnake.ext import commands
from relationships import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = disnake.Intents(message_content=True, members=True, guilds=True)
bot = commands.Bot(intents=intents, command_prefix='$', sync_commands_debug=True)

help_str = open(os.path.join('.', 'assets', 'help.txt'), 'r').read()


# TODO update message as it iterates through users when initially creating hierarchy
@bot.slash_command(description="Apply any existing hierarchies! They may not get applied when first described.", dm_permission=False)
async def updateheirarchy(inter):
    await inter.response.send_message("Okay! Updating roles...")
    json_contents = readJson(inter.guild.id)[0]
    role_count = len(json_contents)
    if role_count:
        for role_index, role in enumerate(json_contents.keys()):
            role = findRole(inter, role)
            for user_index, user in enumerate(inter.guild.members):
                await inter.edit_original_message(
                    content="Okay! Updating {}, role #{} out of {} roles in hierarchies on the server."
                            "\nCurrently processing user {}, #{} out of {}".format(role.mention, role_index + 1,
                                                                                   role_count,
                                                                                   user.mention, user_index + 1,
                                                                                   len(inter.guild.members)))
                await UpdateRole(role)
        await inter.edit_original_message(content="Okay! Done updating all {} hierarchied roles on the server!"
                                                  "".format(role_count))
    else:
        await inter.edit_original_message(content="Sorry! No hierarchies to update on the server!")


# TODO option to add list of roles in either argument
@bot.slash_command(description="Makes a hierarchy between the parent and child role.", dm_permission=False)
async def createheirarchy(inter, parent_role: disnake.Role, child_role: disnake.Role):
    if inter.user.guild_permissions.administrator:
        await relationLogic(inter, child_role, parent_role, Relation.Child)
    else:
        await inter.response.send_message("Sorry! You're not an admin, and therefore cannot create that hierarchy!")


# TODO Make functions for disassociate and associate


@bot.slash_command(description="Confused? Use this command if you're not sure how this works.", dm_permission=True)
async def helpheirarchy(inter):
    await DirectMessageUser(inter, help_str)


@bot.slash_command(description="Show all of the hierarchies between roles on the server", dm_permission=False)
async def displayheirarchy(inter):
    result = '***Printing all the hierarchies on {}:***\n\n'.format(inter.guild)
    json_contents = readJson(inter.guild.id)[0]
    keys = json_contents.keys()
    for key in keys:
        keyHierarchies = ''
        children = ''
        parents = ''
        keyHierarchies += '*{} Hierarchies* ---\n'.format(findRole(inter, key).name)
        if not json_contents[key].keys():
            result = 'Sorry! No hierarchies are stored for this server yet!{}**===============**\n'.format(
                keyHierarchies)
        for subkey in json_contents[key].keys():
            match json_contents[key][subkey]:
                case 1:
                    parents += '*{}*\n'.format(findRole(inter, subkey).name)
                case 2:
                    children += '*{}*\n'.format(findRole(inter, subkey).name)
        if children:
            keyHierarchies += '**Children roles**:\n' + children
        if parents:
            keyHierarchies += '**Parent roles**:\n' + parents
        result += '{}\n**===============**\n\n'.format(keyHierarchies)

    await DirectMessageUser(inter, result[:-21])


@bot.event
async def on_member_update(before, after, new_role=None):
    if len(before.roles) < len(after.roles):
        new_role = next(role for role in after.roles if role not in before.roles)
    elif len(before.roles) > len(after.roles):
        new_role = next(role for role in before.roles if role not in after.roles)
    if new_role is not None:
        await UpdateRole(new_role, after)


async def DirectMessageUser(inter, message):
    directmessage = inter.user.dm_channel
    if not directmessage:
        directmessage = await inter.user.create_dm()
    await inter.response.defer()
    await inter.delete_original_message()
    await directmessage.send(message)




async def relationLogic(inter, role1: disnake.Role, role2: disnake.Role, relation_class: int):
    """Whenever one of the slash commands for defining roles is called, this function processes the actual logic
    of storing all the information, since each one is essentially the same process.
    """
    # Probably looking for admin perms + ability to assign/remove roles
    j = RelationDefine(inter.channel.guild.id, role1, role2, relation_class)
    if not j:
        await inter.response.send_message('Sorry! The relation was not able to be saved.')

    status = 'Saved! Now when people get the {} role, they will automatically get the {} role.'.format(role1.mention,
                                                                                                       role2.mention)

    await inter.response.send_message(status)

    match relation_class:
        case 1:
            await UpdateRole(role2, json_contents=j)


def findRole(inter, role_id: str):
    """Given command context and the string of a role, return the value given if it matches a role on the server.
    Else, return an empty string."""
    try:
        if role_id[0] == '<':
            role_id = role_id[3:-1]
        role_id = int(role_id)
        return inter.guild.get_role(role_id)
    except ValueError:
        return None


def RelationCausesLoops(relation):
    """Return true if a paradox is detected.
    Else, return false.
    """
    # TODO implement checking for loops

    # TODO What loops could exist?
    # Disassociating in an odd numbered circle
    # Child and Parent of the same heirarchy
    # Associating and disassociating
    print(relation)


def RelationDefine(guildid, role1, role2, relation_id: int):
    """Given two roles, the ID of the relation to be established and the guild they're in:
    Define a dict object describing the relation, run it through checkRelationParadox()

    If either relation would cause a paradox
    Otherwise,
    """
    relation = {str(role1.id): {str(role2.id): relation_id}}
    if relation_id in Relation:
        converse = {str(role2.id): {str(role1.id): relation_id + 1}}

    if RelationCausesLoops(relation) or RelationCausesLoops(converse):
        return False
    # Call readjson to get information about server relations
    jsoncontents, jsondir = readJson(guildid)
    # Update with the relation, then use that result to update the converse, then return the results
    return updateJson(converse, updateJson(relation, jsoncontents, jsondir), jsondir)


def updateJson(newrelation, json_contents, jsondir):
    """Given the id of a guild and a dictionary object that represents a new relation between two roles:
    Ensure no paradox is created, with checkRelationParadox(),
    then update the json file with the dictionary object.

    Return the updated contents of the json file"""

    # Get the key from the new relation and the stored relations
    key = list(newrelation.keys())[0]
    keys = list(json_contents.keys())

    # Check if role has already been interacted with role
    if key in keys:
        json_contents[key].update(newrelation[key])
    # If the key from new relation doesn't already exist, update the whole json instead
    else:
        json_contents.update(newrelation)

    f = open(jsondir, 'w')
    f.write(json.dumps(json_contents, indent=4))
    f.close()

    return json_contents


def readJson(gid):
    """Given the id of a guild, read the contents of the server-specific json.
    Create an empty json, if it doesn't already exist so the contents are {}.

    Return the contents of the json as a dict object,
    and return the directory of the json file.
    """
    # Find json location, it's all in one folder, with the name of the json based on the guild's id
    jsondir = './guilds/{}.json'.format(gid)

    # Write file for guilds if it doesn't already exist
    if not os.path.exists(jsondir):
        # Write directory for guilds if it doesn't already exist
        if not os.path.exists('./guilds'):
            os.makedirs('./guilds')
        f = open(jsondir, 'w+')
        f.write('{\n}')
        f.close()

    # Open and read the json file
    f = open(jsondir, 'r')
    jsoncontents = json.load(f)
    f.close()

    return jsoncontents, jsondir


async def UpdateRole(recent_role, member=None, json_contents=None):
    """Given a role, update it to follow all relations stored in the guild specific JSON
    member, is member object to update.

    If not provided, then this function will update the role for all users on the server.
    jsoncontents, must be a dict of the guild-specific json. If not provided, then readJson() is called.
    """

    key = str(recent_role.id)
    guild = recent_role.guild
    if member is None:
        member = guild.members
    else:
        member = [member]

    if json_contents is None:
        json_contents = readJson(guild.id)[0]

    if key not in list(json_contents.keys()):
        return

    for target_member in member:
        roles_to_add = []
        roles_to_remove = []
        recent_role_is_present = True if recent_role in target_member.roles else False
        for role_id in json_contents[key]:
            target_role = guild.get_role(int(role_id))
            target_role_is_present = True if target_role in target_member.roles else False
            match json_contents[key][role_id], recent_role_is_present, target_role_is_present:
                # Child of hierarchy:
                # parent present, child missing
                case Relation.Child, True, False:
                    roles_to_add.append(target_role)

                # Parent of hierarchy:
                # parent missing, child present
                case Relation.Parent, False, True:
                    roles_to_remove.append(target_role)

                case Relation.Associated, True, False:
                    roles_to_add.append(target_role)
                case Relation.Associated, False, True:
                    roles_to_add.append(recent_role)

                case Relation.Disassociated, True, True:
                    roles_to_remove.append(target_role)
                case Relation.Disassociated, False, False:
                    roles_to_add.append(target_role)

        print('\n\nChanging roles\n{}'.format(guild))
        if roles_to_add:
            print(roles_to_add)
            for recent_role in roles_to_add:
                await target_member.add_roles(recent_role)
        if roles_to_remove:
            print(roles_to_remove)
            for recent_role in roles_to_remove:
                await target_member.remove_roles(recent_role)

    # TODO make a two part function that removes a specific role-to-role function
    # put considerations for symmetrical relations

    # TODO make a inverse hierarchy. Gotta get rid of those beginner roles.
    # 10 -> 11 = 01
    # 01 -> 11 = 10
    # 10 -> 00 = 00
    # Could make a kmap or something


    # TODO make an need/needed heirarchy. Get rid of roles when their children are gone




bot.run(TOKEN)
