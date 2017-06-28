import private
import requests
import json
import time
import os.path
import discord
import logging

REPORTS_URL = 'https://www.warcraftlogs.com/v1/reports/guild/{0}/{1}/{2}?start={3}&api_key={4}'
ZONES_URL = 'https://www.warcraftlogs.com/v1/zones?api_key={0}'
REPORT_URL = 'https://www.warcraftlogs.com/v1/report/fights/{0}?api_key={1}'
WCL_URL = 'https://www.warcraftlogs.com/reports/{0}'
ZONES = []
REPORTS = []
LAST_TIME = 0
CLIENT = discord.Client()
DISCORD_CHANNEL = None

# logging.basicConfig(level=logging.DEBUG)

def getZones():
    r = requests.get(ZONES_URL.format(private.API_KEY))
    json_zones = r.json()
    zones = []
    for zone in json_zones:
        new_zone = {'id': zone['id'], 'name': zone['name'], 'encounters': []}
        for encounter in zone['encounters']:
            new_zone['encounters'].append({'id': encounter['id'], 'name': encounter['name']})
        zones.append(new_zone)
    return zones

def getReports():
    r = requests.get(REPORTS_URL.format(private.GUILD_NAME, private.SERVER_NAME, private.REGION, LAST_TIME, private.API_KEY))
    json_reports = r.json()
    reports = []
    for report in json_reports:
        reports.append({'id': report['id'], 'title': report['title'], 'author': report['owner']})
    return reports

async def newReport(report):
    r = requests.get(REPORT_URL.format(report['id'], private.API_KEY))
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
    for z in ZONES:
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

    
    message = report['author'] + ' has uploaded a new log. ' + boss + ' is ' + ('not ' if not boss_dead else '') + 'dead' 
    em = discord.Embed(title=report['title'], description=message, url=WCL_URL.format(report['id']))
    await CLIENT.send_message(DISCORD_CHANNEL, message, False, em)

def getTime():
    if not os.path.isfile('lastTime.conf'):
        saveTime()

    with open('lastTime.conf') as f:
        return int(f.read())

def saveTime():
    LAST_TIME = int(time.time() * 1000)
    f = open('lastTime.conf', 'w')
    f.write(str(LAST_TIME))
    f.close()

async def main_loop():
    while True:
        print('Getting reports...')
        reports = getReports()
        for report in reports:
            if not report in REPORTS:
                REPORTS.append(report)
                await newReport(report)
        saveTime()
        time.sleep(5 * 60)

@CLIENT.event
async def on_ready():
    global DISCORD_CHANNEL
    for server in CLIENT.servers:
        for channel in server.channels:
            if channel.name == private.CHANNEL_NAME:
                DISCORD_CHANNEL = channel
                break
            if DISCORD_CHANNEL is not None:
                break
    await main_loop()

if __name__ == '__main__':
    LAST_TIME = getTime()
    print('Getting zones...')
    ZONES = getZones()
    print('Connecting to Discord...')
    CLIENT.run(private.DISCORD_TOKEN)