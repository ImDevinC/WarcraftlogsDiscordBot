import aiohttp

async def getJsonData(url):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(url) as r:
            json_data = await r.json()
            return json_data

async def getAffixes():
    json_affixes = await getJsonData('https://raider.io/api/v1/mythic-plus/affixes?region=US')
    if 'title' in json_affixes:
        return json_affixes['title']
    else:
        return None

async def getHighest(player, realm):
    json_result = await getJsonData('https://raider.io/api/v1/characters/profile?region=us&realm={0}&name={1}&fields=mythic_plus_weekly_highest_level_runs'.format(realm, player))
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
