import private
import json
import os.path, os.rename
import discord
import asyncio
import aiohttp

REPORTS_URL = 'https://www.warcraftlogs.com/v1/reports/guild/{0}/{1}/{2}?start={3}&api_key={4}'
ZONES_URL = 'https://www.warcraftlogs.com/v1/zones?api_key={0}'
REPORT_URL = 'https://www.warcraftlogs.com/v1/report/fights/{0}?api_key={1}'
WCL_URL = 'https://www.warcraftlogs.com/reports/{0}'
TN_IMG_URL = 'https://www.warcraftlogs.com/img/icons/warcraft/zone-{0}.png'

async def getJsonData(url):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(url) as r:
            json_data = await r.json()
            return json_data

async def getZones():
    json_zones = await getJsonData(ZONES_URL.format(private.API_KEY))
    zones = []
    for zone in json_zones:
        if (not 'id' in zone) or (not 'name' in zone) or (not 'encounters' in zone):
            print('Zone is missing information', zone)
            continue
        new_zone = {'id': zone['id'], 'name': zone['name'], 'encounters': []}
        for encounter in zone['encounters']:
            if (not 'id' in encounter) or (not 'name' in encounter):
                print('Encounter is missing information', encounter)
                continue
            new_zone['encounters'].append({'id': encounter['id'], 'name': encounter['name']})
        zones.append(new_zone)
    return zones

async def getReports(start_time):
    json_reports = await getJsonData(REPORTS_URL.format(private.GUILD_NAME, private.SERVER_NAME, private.REGION, start_time, private.API_KEY))
    reports = []
    for report in json_reports:
        if (not 'id' in report) or (not 'title' in report) or (not 'owner' in report) or (not 'start' in report) or (not 'zone' in report):
            print('Report is missing information', report)
            continue
        reports.append({'id': report['id'], 'title': report['title'], 'author': report['owner'], 'time': report['start']})
    return reports

async def newReport(report, zones, client, channel):
    json_report = await getJsonData(REPORT_URL.format(report['id'], private.API_KEY))
    if not 'zone' in json_report:
        print('Unable to get zone from report ' + report['id'])
        return
    zone_id = json_report['zone']
    
    if not 'fights' in json_report:
        print('Unable to get fights from report ' + report['id'])
        return
    
    boss_report = None
    for i in reversed(json_report['fights']):
        if 'boss' in i and 'kill' in i:
            boss_report = i
            break
    
    if boss_report is None:
        print('Unable to get boss information from report ' + report['id'])
        return
    
    boss_id = boss_report['boss']
    boss_dead = boss_report['kill']
    boss = None
    zone = None
    for z in zones:
        if z['id'] == zone_id:
            zone = z['name']
        for encounter in z['encounters']:
            if encounter['id'] == boss_id:
                boss = encounter['name']
                break
        if zone is not None and boss is not None:
            break

    if zone is None or boss is None:
        print('Unable to get fight information for report ' + report['id'])
        return

    saveTime(report['time'])
    message = report['author'] + ' has uploaded a new log for ' + zone + '. ' + boss + ' is ' + ('not ' if not boss_dead else '') + 'dead' 
    em = discord.Embed(title=report['title'], description=message, url=WCL_URL.format(report['id']), color=0x8BC34A if boss_dead else 0xF44336)
    em.set_thumbnail(url=TN_IMG_URL.format(zone_id))
    await client.send_message(channel, embed=em)

def getTime():
    if not os.path.isfile('lastTime.conf'):
        saveTime(0)
        return 0

    with open('lastTime.conf') as f:
        try:
            return int(f.read())
        except Exception as ex:
            saveTime(0)
            return 0

def saveTime(time):
    try:
        f = open('lastTime.tmp', 'w')
        f.write(str(time + 1))
        f.close()
    except Exception as ex:
        print('Unable to save lastTime', ex)
        return
    os.rename('lastTime.tmp', 'lastTime.conf')

async def main_loop(client, channel):
    last_time = getTime()
    print('Getting zones...')
    zones = await getZones()
    if len(zones) == 0:
        print('No zones returned')
        return

    all_reports = []
    while not client.is_closed:
        print('Getting reports...')
        new_reports = await getReports(last_time)
        print('Found ' + str(len(new_reports)) + ' reports')
        for report in new_reports:
            if not report in all_reports:
                all_reports.append(report)
                await newReport(report, zones, client, channel)
        await asyncio.sleep(60 * 5)