import discord
import aiohttp
import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

client = discord.Client()

async def fetch(session, url):
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    

client.run('Mjg0NjU2OTI4MDM3MDExNDU2.C5Gy_Q.9VXU-2zeJwTeUCK_7JNButhmO_U')
