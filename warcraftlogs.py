import private
import requests
import json
import time
import os.path
import discord

REPORTS_URL = 'https://www.warcraftlogs.com/v1/reports/guild/{0}/{1}/{2}?start={3}&api_key={4}'
ZONES_URL = 'https://www.warcraftlogs.com/v1/zones?api_key={0}'
REPORT_URL = 'https://www.warcraftlogs.com/v1/report/fights/{0}?api_key={1}'
WCL_URL = 'https://www.warcraftlogs.com/reports/{0}'
TN_IMG_URL = 'https://www.warcraftlogs.com/img/icons/warcraft/zone-{0}.png'

def getZones():
    try:
        r = requests.get(ZONES_URL.format(private.API_KEY))
    except Exception as ex:
        print('Error getting zones: ', ex)
        return []

    json_zones = r.json()
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

def getReports(start_time):
    try:
        r = requests.get(REPORTS_URL.format(private.GUILD_NAME, private.SERVER_NAME, private.REGION, start_time, private.API_KEY))
    except Exception as ex:
        print('Error getting list of reports', ex)
        return[]

    json_reports = r.json()
    reports = []
    for report in json_reports:
        if (not 'id' in report) or (not 'title' in report) or (not 'owner' in report) or (not 'start' in report) or (not 'zone' in report):
            print('Report is missing information', report)
            continue
        reports.append({'id': report['id'], 'title': report['title'], 'author': report['owner'], 'time': report['start']})
    return reports

async def newReport(report, zones, client, channel):
    try:
        r = requests.get(REPORT_URL.format(report['id'], private.API_KEY))
    except Exception as ex:
        print('Error retrieving report ' + report['id'], ex)
        return

    json_report = r.json()
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
    f = open('lastTime.conf', 'w')
    f.write(str(time + 1))
    f.close()

async def main_loop(client, channel):
    last_time = getTime()
    print('Getting zones...')
    zones = getZones()
    if len(zones) == 0:
        print('No zones returned')
        return

    all_reports = []
    while True:
        print('Getting reports...')
        new_reports = getReports(last_time)
        print('Found ' + str(len(new_reports)) + ' reports')
        for report in new_reports:
            if not report in all_reports:
                all_reports.append(report)
                await newReport(report, zones, client, channel)
        time.sleep(5 * 60)