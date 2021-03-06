import aiohttp

BASE_URL = 'https://raider.io/api/v1/'

# https://mythicpl.us/#sched
WEEKLY_AFFIXES = [
    ['Raging', 'Volcanic', 'Tyrannical'],
    ['Teeming', 'Explosive', 'Fortified'],
    ['Bolstering', 'Grievous', 'Tyrannical'],
    ['Sanguine', 'Volcanic', 'Fortified'],
    ['Bursting', 'Skittish', 'Tyrannical'],
    ['Teeming', 'Quaking', 'Fortified'],
    ['Raging', 'Necrotic', 'Tyrannical'],
    ['Bolstering', 'Skittish', 'Fortified'],
    ['Teeming', 'Necrotic', 'Tyrannical'],
    ['Sanguine', 'Grievous', 'Fortified'],
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
    return {'success': True, 'name': json_result['name'], 'realm': json_result['realm'], 'dungeon': dungeon['dungeon'], 'highest': dungeon['mythic_level'], 'url': dungeon['url']}

async def getRanks(player, realm):
    json_result = await getJsonData(BASE_URL + 'characters/profile', {'region': 'US', 'realm': realm, 'name': player, 'fields': 'mythic_plus_ranks'})
    if json_result is None:
        return {'success': False, 'message': 'Unable to get Mythic+ ranks'}
    if 'error' in json_result and 'message' in json_result:
        return {'success': False, 'message': json_result['message']}
    if not 'name' in json_result or not 'mythic_plus_ranks' in json_result or not 'profile_url' in json_result or not 'realm' in json_result:
        return {'success': False, 'message': 'Invalid information returned'}
    ranks = json_result['mythic_plus_ranks']
    if not 'overall' in ranks or not 'dps' in ranks or not 'healer' in ranks or not 'tank' in ranks or not 'class' in ranks or not 'class_dps' in ranks or not 'class_healer' in ranks or not 'class_tank' in ranks:
        return {'success': False, 'message': 'Invalid information returned'}
    return {'success': True, 'name': json_result['name'], 'class': json_result['class'], 'spec': json_result['active_spec_role'].lower(), 'url': json_result['profile_url'], 'realm': json_result['realm'], 'rank_overall': ranks['overall'], 'rank_dps': ranks['dps'], 'rank_healing': ranks['healer'], 'rank_tank': ranks['tank'], 'rank_class': ranks['class'], 'rank_class_dps': ranks['class_dps'], 'rank_class_healing': ranks['class_healer'], 'rank_class_tank': ranks['class_tank']}