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