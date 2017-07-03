import aiohttp

BASE_URL = 'https://raider.io/api/v1/'

# https://mythicpl.us/#sched
WEEKLY_AFFIXES = [
    ['Raging', 'Volcanic', 'Tyrannical'],
    ['Teeming', 'Explosive', 'Fortified'],
    ['Bolstering', 'Grievous', 'Tyrannical'],
    ['Sanguine', 'Volvanic', 'Fortified'],
    ['Bursting', 'Skittish', 'Tyrannical'],
    ['Teeming', 'Quaking', 'Fortified'],
    ['Raging', 'Necrotic', 'Tyrannical'],
    ['Bolstering', 'Skittish', 'Fortified'],
    ['Teeming', 'Nectroic', 'Tyrannical'],
    ['Sanguine', 'Grevious', 'Fortified'],
    ['Bolstering', 'Explosive', 'Tyrannical'],
    ['Bursting', 'Quaking', 'Fortified']
]

async def getJsonData(url, params):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(url, params=params) as r:
            json_data = await r.json()
            return json_data

async def getAffixes():
    json_affixes = await getJsonData(BASE_URL + 'mythic-plus/affixes', {'region': 'US'})
    if json_affixes is None:
        return None
    if not 'title' in json_affixes or not 'affix_details' in json_affixes:
        return None
    affixes = {'this_week': json_affixes['title'], 'next_week': None, 'two_weeks': None}
    this_week = affixes['this_week'].split(', ')
    index = WEEKLY_AFFIXES.index(this_week)
    index += 1
    if index == len(WEEKLY_AFFIXES):
        index = 0
    affixes['next_week'] = ', '.join(WEEKLY_AFFIXES[index])
    index += 1
    if index == len(WEEKLY_AFFIXES):
        index = 0
    affixes['two_weeks'] = ', '.join(WEEKLY_AFFIXES[index])
    return affixes

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
