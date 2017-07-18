import private
import discord
from discord.ext import commands
import warcraftlogs
import mythics
import battlenet
import time
import urllib

MAX_LEVEL = 110
LAST_GHIGHEST = 0
PLAYER_SCORES = {}
BOT_CHANNEL = None

description = '''I'm LogBot! I constantly search for new Warcraft Logs and can provide some other information'''
client = commands.Bot(command_prefix='!', description=description, pm_help=True)

def get_differences(player, realm, overall, class_rank):
    scores = PLAYER_SCORES.get('{0}{1}'.format(player, realm))
    return_scores = None
    if scores is not None:
        overall_world_diff = -1 * (overall['world'] - scores['overall']['world'])
        if overall_world_diff > -1:
            overall_world_diff = '+{0}'.format(overall_world_diff)
        overall_region_diff = -1 * (overall['region'] - scores['overall']['region'])
        if overall_region_diff > -1:
            overall_region_diff = '+{0}'.format(overall_region_diff)
        overall_realm_diff = -1 * (overall['realm'] - scores['overall']['realm'])
        if overall_realm_diff > -1:
            overall_realm_diff = '+{0}'.format(overall_realm_diff)
        class_world_diff =  -1 * (class_rank['world'] - scores['class_rank']['world'])
        if class_world_diff > -1:
            class_world_diff = '+{0}'.format(class_world_diff)
        class_region_diff = -1 * (class_rank['region'] - scores['class_rank']['region'])
        if class_region_diff > -1:
            class_region_diff = '+{0}'.format(class_region_diff)
        class_realm_diff = -1 * (class_rank['realm'] - scores['class_rank']['realm'])
        if class_realm_diff > -1:
            class_realm_diff = '+{0}'.format(class_realm_diff)
        return_scores = [[overall_world_diff, overall_region_diff, overall_realm_diff], [class_world_diff, class_region_diff, class_realm_diff]]
    PLAYER_SCORES['{0}{1}'.format(player, realm)] = {'overall': overall, 'class_rank': class_rank}
    return return_scores

async def warcraftlogs_parser(client):
    await client.wait_until_ready()
    channel = discord.Object(id=private.DISCORD_CHANNEL)
    if channel is not None:
        await warcraftlogs.main_loop(client, channel)

async def getHighest(character, realm):
    realm = realm.lower().replace('\'', '').replace(' ', '-')
    details = await mythics.getHighest(character, realm)
    return details

@client.command()
async def affixes():
    '''Shows this week\'s affixes'''
    affixes = await mythics.getAffixes()
    if affixes is not None:
        em = discord.Embed(title='Weekly Affixes', description='This week: {0}\nNext week: {1}'.format(affixes['this_week'], affixes['next_week']), url='https://mythicpl.us')
        em.set_footer(text='Information provided by mythicpl.us')
        if BOT_CHANNEL is None:
            await client.say(embed=em)
        else:
            await client.send_message(BOT_CHANNEL, embed=em)
    else:
        if BOT_CHANNEL is None:
            await client.say('Sorry, I couldn\'t get the affixes for some reason. Try again later')
        else:
            await client.send_message(BOT_CHANNEL, 'Sorry, I couldn\'t get the affixes for some reason. Try again later')

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
        if BOT_CHANNEL is None:
            await client.say('Character name is required')
        else:
            await client.send_message(BOT_CHANNEL, 'Character name is required')
        return

    result = await getHighest(character, realm)
    if result['success'] is False:
        message = result['message']
        if BOT_CHANNEL is None:
            await client.say(message)
        else:
            await client.send_message(BOT_CHANNEL, message)
        return
    
    message = '{0} has completed a +{1} {2}'.format(result['name'], result['highest'], result['dungeon'])
    em = discord.Embed(title='{0} on {1}'.format(result['name'], result['realm']), description=message, url=result['url'])
    em.set_footer(text='Information provided by raider.io', icon_url='https://raider.io/images/favicon.png')
    if BOT_CHANNEL is None:
        await client.say(embed=em)
    else:
        await client.send_message(BOT_CHANNEL, embed=em)
    
@client.command(help='Show the current Mythic+ rank for <character>\nIf character is not on ' + private.DEFAULT_REALM + ', use <character> <realm>')
async def rank(*, character: str):
    '''Show the current Mythic+ rank for <character>'''
    character = character.strip()
    realm = private.DEFAULT_REALM
    if ' ' in character:
        results = character.split(' ', maxsplit=1)
        character = results[0]
        realm = results[1]
    
    if character is None:
        if BOT_CHANNEL is None:
            await client.say('Character name is required')
        else:
            await client.send_message(BOT_CHANNEL, 'Character name is required')
        return

    ranks = await mythics.getRanks(character, realm)
    if ranks['success'] == False:
        if BOT_CHANNEL is None:
            await client.say(ranks['message'])
        else:
            await client.send_message(BOT_CHANNEL, ranks['message'])
        return

    spec = ranks['spec']
    if spec == 'dps':
        print_spec = 'DPS'
    elif spec == 'healing':
        print_spec = 'Healing'
    elif spec == 'tank':
        print_spec = 'Tanking'
    over = ranks['rank_' + spec]
    class_rank = ranks['rank_class_' + spec]
    diffs = get_differences(ranks['name'], ranks['realm'], over, class_rank)
    if diffs is None:
        message = '**Overall {0}**\nWorld: {1}\tRegion: {2}\tRealm: {3}\n\n**{4} {0}**\nWorld: {5}\tRegion: {6}\tRealm: {7}'.format(print_spec, over['world'], over['region'], over['realm'], ranks['class'], class_rank['world'], class_rank['region'], class_rank['realm'])
    else:
        message = '**Overall {0}**\nWorld: {1} ({8})\tRegion: {2} ({9})\tRealm: {3} ({10})\n\n**{4} {0}**\nWorld: {5} ({11})\tRegion: {6} ({12})\tRealm: {7} ({13})'.format(print_spec, over['world'], over['region'], over['realm'], ranks['class'], class_rank['world'], class_rank['region'], class_rank['realm'], diffs[0][0], diffs[0][1], diffs[0][2], diffs[1][0], diffs[1][1], diffs[1][2])
    em = discord.Embed(title='{0} on {1}'.format(ranks['name'], ranks['realm']), description=message, url=ranks['url'])
    em.set_footer(text='Information provided by raider.io', icon_url='https://raider.io/images/favicon.png')
    if BOT_CHANNEL is None:
        await client.say(embed=em)
    else:
        await client.send_message(BOT_CHANNEL, embed=em)

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
        if BOT_CHANNEL is None:
            await client.say('You\'re doing that too much, wait {0} seconds'.format(60 - (now - LAST_GHIGHEST)))
        else:
            await client.send_message(BOT_CHANNEL, 'You\'re doing that too much, wait {0} seconds'.format(60 - (now - LAST_GHIGHEST)))
        return
    LAST_GHIGHEST = now
    if BOT_CHANNEL is None:
        await client.say('Getting highest keys for members of {0} on {1}'.format(guild, realm))
    else:
        await client.send_message(BOT_CHANNEL, 'Getting highest keys for members of {0} on {1}'.format(guild, realm))
    result = await battlenet.getGuildMembers(guild, realm)
    if result['success'] == False:
        await client.say(result['message'])
        LAST_GHIGHEST = 0
        return
    for member in result['members']:
        if member['level'] < MAX_LEVEL:
            continue
        result = await getHighest(member['name'], member['realm'])
        if result['success'] is False or result['highest'] < 1:
            continue
        message += '\n{0} has completed a +{1} {2}'.format(result['name'], result['highest'], result['dungeon'])
    em = discord.Embed(title='{0} on {1}'.format(guild, realm), description=message)
    em.set_footer(text='Information provided by raider.io', icon_url='https://raider.io/images/favicon.png')
    if BOT_CHANNEL is None:
        await client.say(embed=em)
    else:
        await client.send_message(BOT_CHANNEL, embed=em)

@client.command(hidden=True)
async def setchannel(channel_id):
    global BOT_CHANNEL
    if str(channel_id) == '-1':
        BOT_CHANNEL = None
    else:
        BOT_CHANNEL = client.get_channel(channel_id)

@client.event
async def on_ready():
    global BOT_CHANNEL
    print('Logged in')
    if private.DISCORD_BOT_CHANNEL is not None:
        BOT_CHANNEL = client.get_channel(private.DISCORD_BOT_CHANNEL)

if __name__ == '__main__':
    print('Connecting to Discord...')
    client.loop.create_task(warcraftlogs_parser(client))
    client.run(private.DISCORD_TOKEN)