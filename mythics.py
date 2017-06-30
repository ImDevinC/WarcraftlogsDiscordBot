import aiohttp

BASE_URL = 'https://raider.io/api/v1/'

async def getJsonData(url, params):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(url, params=params) as r:
            json_data = await r.json()
            return json_data

async def getAffixes():
    json_affixes = await getJsonData(BASE_URL + 'mythic-plus/affixes', {'region': 'US'})
    if not json_affixes is None and 'title' in json_affixes:
        return json_affixes['title']
    else:
        return None

async def getHighest(player, realm):
    json_result = await getJsonData(BASE_URL + 'characters/profile', {'region': 'US', 'realm': realm, 'name': player, 'fields': 'mythic_plus_weekly_highest_level_runs'})
    if json_result is None:
        return {'success': False, 'message': 'Unable to get Mythic+ data'}
    if 'error' in json_result and 'message'in json_result:
        return {'success': False, 'message': json_result['message']}
    if not 'name' in json_result or not 'mythic_plus_weekly_highest_level_runs' in json_result:
        return {'success': False, 'message': 'Invalid information returned'}
    if len(json_result['mythic_plus_weekly_highest_level_runs']) == 0:
        return {'success': True, 'name': json_result['name'], 'highest': 0}
    dungeon = json_result['mythic_plus_weekly_highest_level_runs'][0]
    if not 'dungeon' in dungeon or not 'mythic_level' in dungeon or not 'url' in dungeon:
        return {'success': False, 'message': 'Invalid information returned'}
    return {'success': True, 'name': json_result['name'], 'dungeon': dungeon['dungeon'], 'highest': dungeon['mythic_level'], 'url': dungeon['url']}
