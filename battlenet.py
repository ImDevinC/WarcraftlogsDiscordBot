import aiohttp
import private

BASE_URL = 'https://us.api.battle.net/wow/'

async def getJsonData(url):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(url) as r:
            json_data = await r.json()
            return json_data

async def getGuildMembers(guild, realm):
    json_guild = await getJsonData(BASE_URL + '/guild/{0}/{1}?fields=members&local=en_US&apikey={2}'.format(realm, guild, private.BNET_API))
    if 'reason' in json_guild:
        return {'success': False, 'message': json_guild['reason']}
    if not 'members' in json_guild:
        return {'success': False, 'message': 'Unable to get guild members'}
    members = []
    for member in json_guild['members']:
        if not 'character' in member:
            continue
        member = member['character']
        if not 'name' in member or not 'realm' in member or not 'level' in member:
            continue
        members.append({'name': member['name'], 'realm': member['realm'], 'level': member['level']})
    return {'success': True, 'members': sorted(members, key=lambda l: l['name'])}