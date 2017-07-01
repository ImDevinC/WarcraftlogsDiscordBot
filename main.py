import private
import discord
from discord.ext import commands
import warcraftlogs
import mythics
import battlenet
import time

MAX_LEVEL = 110
LAST_GHIGHEST = 0

description = '''I'm LogBot! I constantly search for new Warcraft Logs and can provide some other information'''
client = commands.Bot(command_prefix='!', description=description, pm_help=True)

async def warcraftlogs_parser(client):
    await client.wait_until_ready()
    channel = discord.Object(id=private.DISCORD_CHANNEL)
    if channel is not None:
        await warcraftlogs.main_loop(client, channel)

async def getHighest(character, realm):
    realm = realm.lower().replace('\'', '').replace(' ', '-')
    details = await mythics.getHighest(character, realm)
    if details['success'] == False:
        message = details['message']
    elif details['highest'] == 0:
        message = details['name'] + ' has not completed a Mythic+ this week'
    else:
        message = details['name'] + ' has completed a ' + details['dungeon'] + ' +' + str(details['highest'])
    return message

@client.command()
async def affixes():
    '''Shows this week\'s affixes'''
    affixes = await mythics.getAffixes()
    if affixes is not None:
        await client.say('This weeks affixes are: ' + affixes)
    else:
        await client.say('Sorry, I couldn\'t get the affixes for some reason. Try again later')

@client.command(help='Show the highest level Mythic+ completed by <character>.\nIf character is not on ' + private.DEFAULT_REALM + ', use <character> <realm>')
async def highest(*, character: str):
    '''Show the highest level Mythic+ completed by <character>'''
    character = character.strip()
    realm = private.DEFAULT_REALM
    if ' ' in character:
        results = character.split(' ', maxsplit=1)
        character = results[0]
        realm = results[1]
    
    if character is None:
        await client.say('Character name is required')
        return

    message = await getHighest(character, realm)
    await client.say(message)

@client.command(help='Show the highest level Mythic+ completed by all characters in <guild>\nIf guild is not on ' + private.SERVER_NAME + ', use "<guild>" "<realm>"')
async def ghighest(*, guild: str = None):
    global LAST_GHIGHEST
    '''Show the highest level Mythic+ completed by all characters in <guild>'''
    realm = private.DEFAULT_REALM
    if guild == None or guild == '':
        guild = private.GUILD_NAME
    guild = guild.strip()
    realm = private.SERVER_NAME
    message = ''
    if '" ' in guild:
        result = guild.split('" ', maxsplit=1)
        guild = result[0].strip('"')
        realm = result[1].strip('"')
    now = int(time.time())
    if now - LAST_GHIGHEST < 60:
        await client.say('You\'re doing that too much, wait {0} seconds'.format(60 - (now - LAST_GHIGHEST)))
        return
    LAST_GHIGHEST = now
    await client.say('Getting highest keys for members of {0} on {1}'.format(guild, realm))
    result = await battlenet.getGuildMembers(guild, realm)
    if result['success'] == False:
        await client.say(result['message'])
        LAST_GHIGHEST = 0
        return
    for member in result['members']:
        if member['level'] < MAX_LEVEL:
            continue
        result = await getHighest(member['name'], member['realm'])
        if 'has not completed a Mythic+ this week' in result or 'Could not find requested character' in result:
            continue
        message += '\n{0}'.format(result)
    await client.say(message)

@client.event
async def on_ready():
    print('Logged in')

if __name__ == '__main__':
    print('Connecting to Discord...')
    client.loop.create_task(warcraftlogs_parser(client))
    client.run(private.DISCORD_TOKEN)