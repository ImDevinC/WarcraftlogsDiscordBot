import private
import discord
import warcraftlogs
import time

CLIENT = discord.Client()
DISCORD_CHANNEL = None

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
    if DISCORD_CHANNEL is not None:
        await warcraftlogs.main_loop(CLIENT, DISCORD_CHANNEL)

if __name__ == '__main__':
    print('Connecting to Discord...')
    CLIENT.run(private.DISCORD_TOKEN)