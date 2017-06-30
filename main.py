import private
import discord
from discord.ext import commands
import warcraftlogs
import mythics
import asyncio

# client = discord.Client()
description = '''I'm LogBot! I constantly search for new Warcraft Logs and can provide some other information'''
client = commands.Bot(command_prefix='!', description=description)

async def warcraftlogs_parser(client):
    await client.wait_until_ready()
    channel = discord.Object(id=private.DISCORD_CHANNEL)
    if channel is not None:
        await warcraftlogs.main_loop(client, channel)

@client.command(description='Shows this week\'s affixes')
async def affixes():
    affixes = await mythics.getAffixes()
    if affixes is not None:
        await client.say('This weeks affixes are: ' + affixes)
    else:
        await client.say('Sorry, I couldn\'t get the affixes for some reason. Try again later')

@client.command(description='Get\'s characters highest mythic+ for this week')
async def highest(*, character: str):
    character = character.strip()
    realm = 'borean-tundra'
    if ' ' in character:
        results = character.split(' ', maxsplit=1)
        character = results[0]
        realm = results[1].replace('\'', '').replace(' ', '-')


    details = await mythics.getHighest(character, realm)
    if details['success'] == False:
        message = details['message']
    elif details['highest'] == 0:
        message = details['name'] + ' has not completed a Mythic+ this week'
    else:
        message = details['name'] + ' has completed a ' + details['dungeon'] + ' +' + str(details['highest'])
    await client.say(message)

@client.event
async def on_ready():
    print('Logged in')

if __name__ == '__main__':
    print('Connecting to Discord...')
    client.loop.create_task(warcraftlogs_parser(client))
    client.run(private.DISCORD_TOKEN)