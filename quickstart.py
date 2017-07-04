#TODO spread out functions into different files
from __future__ import print_function
import httplib2
import os
import re, string; pattern = re.compile('[\W_]+')


import discord
import aiohttp
import asyncio

import telegram

from datetime import datetime
from datetime import timedelta

from apiclient import discovery
from oauth2client import client as Oclient
from oauth2client import tools
from oauth2client.file import Storage

from pytesseract import image_to_string
from pytesseract import cleanup_colors
from pytesseract import common_color
from PIL import Image
import PIL.ImageOps
import imghdr

import subprocess

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'
CURRENT_DIR = '/home/donald/HK47'
TRUSTED_IDS = ['278708481995833354','279810303170969620','271379542688399362','278723003146174465','233963211588632576','260836495236005888','232074884086366208']

client = discord.Client()
tele_bot = None
medal_channels_ = []
scan_channels_ = []
udex_channels_ = []
update_index = 0

temp_gather_list = {}

SHEET_ENUM = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB',
              'AC', 'AD', 'AE', 'AF', 'AG', 'AH']
service = None

POKE_NAMES = ["Bulbasaur","Ivysaur","Venusaur","Charmander","Charmeleon","Charizard","Squirtle","Wartortle","Blastoise","Caterpie","Metapod","Butterfree",
              "Weedle","Kakuna","Beedrill","Pidgey","Pidgeotto","Pidgeot","Rattata","Raticate","Spearow","Fearow","Ekans","Arbok","Pikachu","Raichu",
              "Sandshrew","Sandslash","Nidoran♀","Nidorina","Nidoqueen","Nidoran♂","Nidorino","Nidoking","Clefairy","Clefable","Vulpix","Ninetales",
              "Jigglypuff","Wigglytuff","Zubat","Golbat","Oddish","Gloom","Vileplume","Paras","Parasect","Venonat","Venomoth","Diglett","Dugtrio",
              "Meowth","Persian","Psyduck","Golduck","Mankey","Primeape","Growlithe","Arcanine","Poliwag","Poliwhirl","Poliwrath","Abra","Kadabra",
              "Alakazam","Machop","Machoke","Machamp","Bellsprout","Weepinbell","Victreebel","Tentacool","Tentacruel","Geodude","Graveler","Golem",
              "Ponyta","Rapidash","Slowpoke","Slowbro","Magnemite","Magneton","Farfetch'd","Doduo","Dodrio","Seel","Dewgong","Grimer","Muk","Shellder",
              "Cloyster","Gastly","Haunter","Gengar","Onix","Drowzee","Hypno","Krabby","Kingler","Voltorb","Electrode","Exeggcute","Exeggutor","Cubone",
              "Marowak","Hitmonlee","Hitmonchan","Lickitung","Koffing","Weezing","Rhyhorn","Rhydon","Chansey","Tangela","Kangaskhan","Horsea","Seadra",
              "Goldeen","Seaking","Staryu","Starmie","Mr. Mime","Scyther","Jynx","Electabuzz","Magmar","Pinsir","Tauros","Magikarp","Gyarados","Lapras",
              "Ditto","Eevee","Vaporeon","Jolteon","Flareon","Porygon","Omanyte","Omastar","Kabuto","Kabutops","Aerodactyl","Snorlax","Articuno","Zapdos",
              "Moltres","Dratini","Dragonair","Dragonite","Mewtwo","Mew","Chikorita","Bayleef","Meganium","Cyndaquil","Quilava","Typhlosion","Totodile",
              "Croconaw","Feraligatr","Sentret","Furret","Hoothoot","Noctowl","Ledyba","Ledian","Spinarak","Ariados","Crobat","Chinchou","Lanturn","Pichu",
              "Cleffa","Igglybuff","Togepi","Togetic","Natu","Xatu","Mareep","Flaaffy","Ampharos","Bellossom","Marill","Azumarill","Sudowoodo","Politoed",
              "Hoppip","Skiploom","Jumpluff","Aipom","Sunkern","Sunflora","Yanma","Wooper","Quagsire","Espeon","Umbreon","Murkrow","Slowking","Misdreavus",
              "Unown","Wobbuffet","Girafarig","Pineco","Forretress","Dunsparce","Gligar","Steelix","Snubbull","Granbull","Qwilfish","Scizor","Shuckle",
              "Heracross","Sneasel","Teddiursa","Ursaring","Slugma","Magcargo","Swinub","Piloswine","Corsola","Remoraid","Octillery","Delibird","Mantine",
              "Skarmory","Houndour","Houndoom","Kingdra","Phanpy","Donphan","Porygon2","Stantler","Smeargle","Tyrogue","Hitmontop","Smoochum","Elekid",
              "Magby","Miltank","Blissey","Raikou","Entei","Suicune","Larvitar","Pupitar","Tyranitar","Lugia","Ho-Oh","Celebi"]

'''POKE_FINAL = {"Bulbasaur":"Venusaur", "Squirtle":"Blastoise", "Charmander":"Charizard", "Caterpie":"Butterfree", "Weedle":"Beedrill", "Pidgey":"Pidgeot", 
              "Rattata":"Raticate"}'''

'''POKE_GAMUT = {"Bulbasaur","Ivysaur","Venusaur","Charmander","Charmeleon","Charizard","Squirtle","Wartortle","Blastoise","Caterpie","Metapod","Butterfree",
              "Weedle","Kakuna","Beedrill","Pidgey","Pidgeotto","Pidgeot","Rattata","Raticate","Spearow","Fearow","Ekans","Arbok","Pikachu","Raichu",
              "Sandshrew","Sandslash","Nidoran♀","Nidorina","Nidoqueen","Nidoran♂","Nidorino","Nidoking","Clefairy","Clefable","Vulpix","Ninetales",
              "Jigglypuff","Wigglytuff","Zubat","Golbat","Oddish","Gloom","Vileplume","Paras","Parasect","Venonat","Venomoth","Diglett","Dugtrio",
              "Meowth","Persian","Psyduck","Golduck","Mankey","Primeape","Growlithe","Arcanine","Poliwag","Poliwhirl","Poliwrath","Abra","Kadabra",
              "Alakazam","Machop","Machoke","Machamp","Bellsprout","Weepinbell","Victreebel","Tentacool","Tentacruel","Geodude","Graveler","Golem",
              "Ponyta","Rapidash","Slowpoke","Slowbro","Magnemite","Magneton","Farfetch'd","Doduo","Dodrio","Seel","Dewgong","Grimer","Muk","Shellder",
              "Cloyster","Gastly","Haunter","Gengar","Onix","Drowzee","Hypno","Krabby","Kingler","Voltorb","Electrode","Exeggcute","Exeggutor","Cubone",
              "Marowak","Hitmonlee","Hitmonchan","Lickitung","Koffing","Weezing","Rhyhorn","Rhydon","Chansey","Tangela","Kangaskhan","Horsea","Seadra",
              "Goldeen","Seaking","Staryu","Starmie","Mr. Mime","Scyther","Jynx","Electabuzz","Magmar","Pinsir","Tauros","Magikarp","Gyarados","Lapras",
              "Ditto","Eevee","Vaporeon","Jolteon","Flareon","Porygon","Omanyte","Omastar","Kabuto","Kabutops","Aerodactyl","Snorlax","Articuno","Zapdos",
              "Moltres","Dratini","Dragonair","Dragonite","Mewtwo","Mew","Chikorita","Bayleef","Meganium","Cyndaquil","Quilava","Typhlosion","Totodile",
              "Croconaw","Feraligatr","Sentret","Furret","Hoothoot","Noctowl","Ledyba","Ledian","Spinarak","Ariados","Crobat","Chinchou","Lanturn","Pichu",
              "Cleffa","Igglybuff","Togepi","Togetic","Natu","Xatu","Mareep","Flaaffy","Ampharos","Bellossom","Marill","Azumarill","Sudowoodo","Politoed",
              "Hoppip","Skiploom","Jumpluff","Aipom","Sunkern","Sunflora","Yanma","Wooper","Quagsire","Espeon","Umbreon","Murkrow","Slowking","Misdreavus",
              "Unown","Wobbuffet","Girafarig","Pineco","Forretress","Dunsparce","Gligar","Steelix","Snubbull","Granbull","Qwilfish","Scizor","Shuckle",
              "Heracross","Sneasel","Teddiursa","Ursaring","Slugma","Magcargo","Swinub","Piloswine","Corsola","Remoraid","Octillery","Delibird","Mantine",
              "Skarmory","Houndour","Houndoom","Kingdra","Phanpy","Donphan","Porygon2","Stantler","Smeargle","Tyrogue","Hitmontop","Smoochum","Elekid",
              "Magby","Miltank","Blissey","Raikou","Entei","Suicune","Larvitar","Pupitar","Tyranitar","Lugia","Ho-Oh","Celebi"}'''

waiting_ = 0
collecting_ = False
queue_ = 0

XP_BY_LEVEL = [0,0,1000,3000,6000,10000,15000,21000,28000,36000,45000,55000,65000,75000,85000,100000,120000,140000,160000,
               185000,210000,260000,335000,435000,560000,710000,900000,1100000,1350000,1650000,2000000,2500000,3000000,3750000,
               4750000,6000000,7500000,9500000,12000000,15000000,20000000]
user_list_index = {}
user_names = ['error', 'junk']
medal_list_index = {}
commands = {}

#basic async url fetch used for fetching discord message attachments
async def fetch(session, url):
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()

#parses command to command dict
async def parse_command(message):
    if message.content.split()[0] in commands.keys():
        await commands[message.content.split()[0]](message)
    else:
        await client.send_message(message.channel, 'Critique: Invalid command.')
        
async def parse_scan(message):
    ret = ['','']
    spl = []
    debug_print = '%s'%(message.embeds)
    f_d = ''.join(s for s in "%s"%(debug_print) if s in string.printable)
    print(f_d)
    if not message.content:
        spl = message.embeds[0]['title'].split()
        text = message.embeds[0]['title']
    else:
        spl = message.content.split()
        text = message.content
    print([s.encode('ascii', 'ignore') for s in spl])
    if len(spl) < 2:
        return ret
    prog = re.compile('-?[\d]{1,2}\.[\d]{1,15},\s*?-?[\d]{1,3}\.[\d]{1,15}')
    
    for word in spl:
        f_s = ''.join(s for s in "%s"%(word) if s in string.ascii_letters).replace(' ','')
        print(f_s)
        if f_s.capitalize() in POKE_NAMES:
            ret[0] = f_s.capitalize()
            print(f_s.capitalize())
            break
    if prog.findall(text):
        ret[1] = prog.findall(text)[0].replace(' ','')
        print(prog.findall(text)[0])
    return ret
    
#for use on non-threadsafe operations that may take a great deal of time
async def dumb_wait(func=None, arg=None):
    for i in range(0,100):
       if waiting_:
           await asyncio.sleep(1)
       else:
           return i

async def image_channel(message):
    global queue_, waiting_

    plID = message.author.id
    ts = datetime.now()

    if plID not in user_list_index.keys():
        await client.send_message(message.channel, 'Advice: Please ?register your username before uploading.')
        return

    plName = user_names[user_list_index[plID]]
    #create folders if they don't exist
    pathPrefix = "%s/%s" % (CURRENT_DIR,week_prefix())
    if not os.path.exists(pathPrefix):
        os.makedirs(pathPrefix)
    pathPrefix = "%s/%s" % (pathPrefix,plName)
    if not os.path.exists(pathPrefix):
        os.makedirs(pathPrefix)
    if not os.path.exists("%s/%s" %(pathPrefix, 'temp')):
        os.makedirs("%s/%s" %(pathPrefix, 'temp'))
    if not os.path.exists("%s/%s" %(pathPrefix, 'error')):
        os.makedirs("%s/%s" %(pathPrefix, 'error'))
    updates = []
    for att in message.attachments:
        with aiohttp.ClientSession() as session:
            async with session.get(att['url']) as resp:
                pic = await resp.read()
                ts = message.timestamp
                path = "%s/%s/%s%s" % (pathPrefix,'temp',ts.isoformat(sep='T'),att['filename'])
                with open(path, "wb") as f:
                    f.write(pic)
                if imghdr.what(path) is None:
                    await client.send_message(message.channel, 'Critique: %s is not an image.' % (att['filename']))
                    continue
        if waiting_:
            await dumb_wait()
        #waiting_ = 1
        #await asyncio.sleep(0)
        data = await read_image(path)
        await asyncio.sleep(0)
        #waiting_ = 0
        update = parse_data(data)
        if 'medal' not in update.keys():
            await client.send_message(message.channel, 'Lamentation: Error reading image %s from %s.' % (att['filename'], plName))
            path = "%s/%s/%s%s" % (pathPrefix,'error',ts.isoformat(sep='T'),att['filename'])
            with open(path, "wb") as f:
                f.write(pic)
            continue
                
        if 'value' not in update.keys() or update['value'] == '0':
            await client.send_message(message.channel, "Lamentation: Error finding value for %s in %s's %s.\nAdvice: Please make sure there are no sparkles covering the number in your screenshot." % (update['medal'], plName,att['filename']))
            path = "%s/%s/%s%s" % (pathPrefix,'error',ts.isoformat(sep='T'),att['filename'])
            with open(path, "wb") as f:
                f.write(pic)
            continue
        else:
            path = "%s/%s%s.png" % (pathPrefix,update['medal'],update['value'])
            with open(path, "wb") as f:
                f.write(pic)
        
        updates.append(update)
    if waiting_:
        await dumb_wait()
    waiting_ = 1
    await asyncio.sleep(0)
    await update_doc(message.author.id, updates, message)
    await asyncio.sleep(0)
    waiting_ = 0


def send_telegram(command):
    proc = subprocess.run(command,stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    return (proc.returncode, proc.stderr, proc.stdout)

#Niantic killed sniping so no longer useful
async def scan_channel(message):
    global update_index
    daChannel = '-218367851'
    
    #filtered = ''.join(s for s in "%s"%(message.embeds) if s in string.printable)
    #print(filtered)
    snipe = await parse_scan(message)
    if not snipe[0]:
        print('error parsing scan')
        return
    command = ["/bin/telegram-cli", "-WRC"]
    s_com = command + ["-e", 'msg Relays "/snipe %s,%s"'%(snipe[0],snipe[1])]
    print(s_com)
    status, error_string, output = send_telegram(s_com)
    if status:
        return
        #errors = get_errors(error_string)
        #TODO
    #description = message.embeds[0]['description']
    await asyncio.sleep(25)
    l_com = command + ["-e", 'msg Relays "/logs"']
    status, error_string, output = send_telegram(l_com)
    if status:
        return
    
    await asyncio.sleep(2)
    l_com = command + ['-f', "-e", 'msg Relays "test"']
    status, error_string, output = send_telegram(l_com)
    if status:
        return
    
    ret = [s for s in output.decode(errors='ignore').split('\n') if 'PKMN' in s and snipe[0] in s]
    if ret:
        for r in ret:
            print(r)
            await client.send_message(message.channel, r)
    #print(updates)
    #print(update_index)
    return

async def udex_channel(message):
    global queue_, waiting_

    plID = message.author.id
    ts = datetime.now()

    '''if plID not in user_list_index.keys():
        await client.send_message(message.channel, 'Advice: Please ?register your username before uploading.')
        return
    '''
    plName = user_names[user_list_index[plID]]
    #create folders if they don't exist
    pathPrefix = "%s/%s" % (CURRENT_DIR,week_prefix())
    if not os.path.exists(pathPrefix):
        os.makedirs(pathPrefix)
    pathPrefix = "%s/%s" % (pathPrefix,plName)
    if not os.path.exists(pathPrefix):
        os.makedirs(pathPrefix)
    if not os.path.exists("%s/%s" %(pathPrefix, 'temp')):
        os.makedirs("%s/%s" %(pathPrefix, 'temp'))
    if not os.path.exists("%s/%s" %(pathPrefix, 'error')):
        os.makedirs("%s/%s" %(pathPrefix, 'error'))
    updates = []
    for att in message.attachments:
        with aiohttp.ClientSession() as session:
            async with session.get(att['url']) as resp:
                pic = await resp.read()
                ts = message.timestamp
                path = "%s/%s/%s%s" % (pathPrefix,'temp',ts.isoformat(sep='T'),att['filename'])
                with open(path, "wb") as f:
                    f.write(pic)
                if imghdr.what(path) is None:
                    await client.send_message(message.channel, 'Critique: %s is not an image.' % (att['filename']))
                    continue
        #if waiting_:
            #await dumb_wait()
        #waiting_ = 1
        #await asyncio.sleep(0)
        try:
            image = Image.open(path)
            
            if len(image.split()) == 4:
                # In case we have 4 channels, lets discard the Alpha.
                # Kind of a hack, should fix in the future some time.
                r, g, b, a = image.split()
                image = Image.merge("RGB", (r, g, b))
        except IOError:
            sys.stderr.write('ERROR: Could not open file "%s"\n' % filename)
            exit(1)
        data = common_color(image)
        print(data)
        #await asyncio.sleep(0)
        #waiting_ = 0
        #update = parse_data(data)
        '''if 'medal' not in update.keys():
            await client.send_message(message.channel, 'Lamentation: Error reading image %s from %s.' % (att['filename'], plName))
            path = "%s/%s/%s%s" % (pathPrefix,'error',ts.isoformat(sep='T'),att['filename'])
            with open(path, "wb") as f:
                f.write(pic)
            continue
                
        if 'value' not in update.keys() or update['value'] == '0':
            await client.send_message(message.channel, "Lamentation: Error finding value for %s in %s's %s.\nAdvice: Please make sure there are no sparkles covering the number in your screenshot." % (update['medal'], plName,att['filename']))
            path = "%s/%s/%s%s" % (pathPrefix,'error',ts.isoformat(sep='T'),att['filename'])
            with open(path, "wb") as f:
                f.write(pic)
            continue
        else:
            path = "%s/%s%s.png" % (pathPrefix,update['medal'],update['value'])
            with open(path, "wb") as f:
                f.write(pic)'''
        
        #updates.append(update)
    '''if waiting_:
        await dumb_wait()
    waiting_ = 1
    await asyncio.sleep(0)
    await update_doc(message.author.id, updates, message)
    await asyncio.sleep(0)
    waiting_ = 0'''

#handles messages
@client.event
async def on_message(message):
    global queue_, waiting_
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    #await gather(message)
    if message.content.startswith('?'):
        if message.content.startswith('???') and message.author.id in TRUSTED_IDS:
            await parse_command(message)
        elif message.channel.id in medal_channels_ or message.channel.id in scan_channels_:
            await parse_command(message)
        return
    
    if message.attachments and collecting_ and message.channel.id in medal_channels_:
        await image_channel(message)
    elif message.channel.id in scan_channels_:
        await scan_channel(message)
    elif message.channel.id in udex_channels_:
        await udex_channel(message)
        return

#when bot comes online
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    for c in client.get_all_members():
        temp_gather_list[c.id] = (c.name, c.nick)

    await gather_update()

    '''if len(medal_channels_) > 0:
        for chan in medal_channels_:
            await client.send_message(chan, 'Statement: Discoonnected and attempting to reconnect.')'''


#returns the current week starting on weekStart
def week_prefix(date=None):
    weekStart = 5 #saturday
    if date is None:
        d = datetime.today()
        d1 = datetime.today()
        d2 = datetime.today()
    else:
        d = date
        d1 = date
        d2 = date
    if d.weekday() < weekStart:
        offset = timedelta(0-(d.weekday() - weekStart + 7))
    else:
        offset = timedelta(0-(d.weekday() - weekStart))
    d1 = d1 + offset
    d2 = d2 + offset + timedelta(days=6)
    #attempted to make date both UNIX and Windows compatible for folder names
    return ("%s-%s-%s--%s-%s-%s" % (d1.month,d1.day,d1.year,d2.month,d2.day,d2.year))

#yeah
def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

#convoluted way to check a number for proper fomatting and find the mode of a shotgun method OCR
def common_num(data, medal):
    modict = {'0' : 0}
    mode = '0'
    index = 0
    xp = 'TOTAL XP' in medal
    for d in data:
        if (not xp and ',' not in d and '.' not in d and len(d) > 3) or d == '1' or (xp and len(d) < 6):
            continue #bad number go to next one
        if d in modict.keys() and d[0] != '0':
            modict[d] += 1
        else:
            modict[d] = 1
        #check formatting and reject improperly formatted numbers
        #could make this function shorter by putting formatting check before modict entry TODO
        if d.count('.') > 2 or d.count(',') > 2 or ('.' in d and xp) or (',' in d and xp):
            print("too many commas or periods or unwanted punctuation in xp")
            modict[d] = 0
            continue
        #because OCR has a hard time with this font's 7s and I'm too lazy to retrain
        if '1' in d and d.replace('1','7') in modict.keys():
            modict[d.replace('1','7')] += 5
        if '2' in d and d.replace('2','9') in modict.keys():
            modict[d.replace('2','9')] += 5
        #checks to see if a period should be a comma
        if '.' in d and len(d.split('.',1)[1].replace(',','').replace('.','')) >= 3 and len(d.split('.',1)[0].replace(',','')) > 1:
            d = d.replace('.',',',1)
            if '.' in d and len(d.split('.',1)[1]) > 1:
                if d in modict.keys():
                    modict[d[:len(d)-len(d.split('.',1)[1])+1]] += 3
                else:
                    modict[d[:len(d)-len(d.split('.',1)[1])+1]] = 3
            elif '.' not in d and len(d.split(',',1)[1]) > 3:
                print("too many numbers after comma after edit")
                modict[d] = 0
            else:
                if d in modict.keys():
                    modict[d] += 3
                else:
                    modict[d] = 3
        #checks to see if there are the correct number of digits before or after the period
        elif '.' in d and (len(d.split('.',1)[1]) == 0 or len(d.split('.',1)[1]) > 1 or len(d.split('.',1)[0]) == 1):
            modict[d] -= 1
        #checks to see if there are the correct number of digits before and after a comma
        if ',' in d and d.count(',') == 1 and len(d.split(',',1)[1]) >= 3 and len(d.split(',',1)[0]) <= 3:
            if '.' in d and len(d.split('.',1)[1]) > 1 and len(d.split(',',1)[1].split('.',1)[0]) == 3:
                if d[:len(d)-len(d.split('.',1)[1])+1] in modict.keys():
                    modict[d[:len(d)-len(d.split('.',1)[1])+1]] += 3
                else:
                    modict[d[:len(d)-len(d.split('.',1)[1])+1]] = 3
            elif '.' not in d and len(d.split(',',1)[1]) > 3:
                print("too many numbers after comma")
                modict[d] = 0
            elif '.' in d and len(d.split(',',1)[1].split('.',1)[0]) != 3:
                modict[d] = 0
            else:
                modict[d] += 3
        elif ',' in d and d.count(',') == 1 and (len(d.split(',',1)[1]) < 3 or len(d.split(',',1)[0]) > 3):
            print("too many numbers before comma or too few numbers after comma")
            modict[d] = 0
        
    #find the mode
    for key in modict.keys():
        less = float(key.replace(',','')) < float(mode.replace(',',''))
        notteen = (float(key.replace(',','')) > 20 or float(key.replace(',','')) < 10)
        eights = mode == key.replace('8','3')
        if modict[key] > modict[mode]:
            mode = key
        elif eights:
            mode = key
        #OCR has trouble with 7s turning into 1s so reject teen numbers when others are possible
        elif modict[key] == modict[mode] and less and notteen and not key == mode.replace('8','3'):
            #if eights:
            mode = key
    print(modict)
    return mode

#grabs the medal and value from OCR data
def parse_data(data):
    newData = {}
    if 'LEVEL' in data[0]:
        #fragile code TODO
        level = int([s[5:7] for s in data[0].split('\n') if 'LEVEL' in s][0])
        newData['medal'] = 'TOTAL XP'
    else:
        level = 0
        for key in medal_list_index:
            if key in data[0] or key in data[len(data)-1]:
                newData['medal'] = key
                #print("%s" % (key))
                #print("%s" % (data.encode('ascii', 'ignore')))
                break
    for d in data:
        print(d.encode('ascii', 'ignore'))
    if 'medal' not in newData.keys():
        print("Error reading image")
        return newData
    if newData['medal'] == 'TOTAL XP':
        #if level > 0:
        #    spl = [s.strip() for s in ''.join(filter(lambda x: x in string.printable, data[0])).replace(' ','').split('\n')]
        #else:
        spl = ''.join(filter(lambda x: x in string.printable, data[len(data)-1])).split()
    else:
        spl = [s.strip() for s in ''.join(filter(lambda x: x in string.printable, data[0])).split('\n')]
        for i in range(1,len(data)-1):
            spl.extend(''.join(filter(lambda x: x in string.printable, data[i])).split())
    
    #the OCR has trouble with 7s
    nums = [s.replace('+','') for s in spl if s.replace(',','').replace('.','').replace('+','').isdigit()]
    
    print("%s" % ([s.encode('ascii', 'backslashreplace') for s in spl]))
    print("%s" % (nums))
    if not nums:
        return newData
    newData['value'] = common_num(nums, newData['medal'])
    if newData['medal'] == 'TOTAL XP' and level > 0:
        newData['value'] = "%s" % (int(newData['value']) + XP_BY_LEVEL[level])
    return newData

#gets Google API credentials
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or iSf the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = Oclient.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

#performs a shotgun OCR analysis 
async def read_image(filename):
    global waiting_
    cartridge = range(0,7)
    try:
        image = Image.open(filename)
        
        if len(image.split()) == 4:
            # In case we have 4 channels, lets discard the Alpha.
            # Kind of a hack, should fix in the future some time.
            r, g, b, a = image.split()
            image = Image.merge("RGB", (r, g, b))
    except IOError:
        sys.stderr.write('ERROR: Could not open file "%s"\n' % filename)
        exit(1)
    output = []
    trimSize = int(image.width/12)
    image = PIL.ImageOps.crop(image,trimSize)
    gauge = int(image.height/3)
    
    #incoming major operation so process other events in queue
    if waiting_:
        await dumb_wait()
    waiting_ = 1
    await asyncio.sleep(0)
    cleanup_colors(image)
    await asyncio.sleep(0)
    output.append(image_to_string(image))
    await asyncio.sleep(0)
    waiting_ = 0
    #hardcoded TODO
    for shot in cartridge:
        spread = shot/8
        imageslot = PIL.ImageOps.fit(image, (image.width, gauge),PIL.Image.ANTIALIAS,0.25,(0.5,spread))
        print(shot)
        if waiting_:
            await dumb_wait()
        waiting_ = 1
        await asyncio.sleep(0)
        output.append(image_to_string(imageslot))
        await asyncio.sleep(0)
        waiting_ = 0
    #hardcoded TODO
    imageBot = PIL.ImageOps.fit(image, (image.width, int(image.height/4)),PIL.Image.ANTIALIAS,0.0,(0.5,1.0))
    output.append(image_to_string(imageBot))
    return(output)

async def update_doc(user, data, message):
    global service
        
    index = user_list_index[user]
    spreadsheetId = '1Tsd1huHdMBcVerodjw-pHa_s4J7GP8xSHyJuL4S-6_s'
    #print("user index before get: %s" % (index))
    medalRangeName = "%s!B%s:AI%s" % (week_prefix(), index, index) # gotta have efficient bandwidth usage
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=medalRangeName).execute()
    medals = result.get('values', [])
    #print("%s" % (medals))
    #index = medal_list_index[data['medal']]
    for entry in data:
        index = medal_list_index[entry['medal']]
        messOne = 'Analysis: %s, %s for %s' % (entry['medal'],entry['value'],message.author.name)
        print("%s,%s,%s" % (entry['medal'],entry['value'],index))
        if float(medals[0][index]) < float(entry['value'].replace(',','')):
            old = float(medals[0][index])
            num = entry['value'].replace(',','')
            medals[0][index] = float(num)
            if old < 1.5:
                messTwo = 'Statement: This appears to be your first upload in this category.'
            else:
                messTwo = 'Statement: This is greater than your previous upload of %s.' % (old)
            if float(num) > old * 1.5 and old > 1.5:
                messTwo = 'Statement: This is significantly greater than your previous upload of %s. If this is not an error, then congratulations are due.' % (old)
        elif float(medals[0][index]) == float(entry['value'].replace(',','')):
            #twiddle thumbs
            print("same as before")
            messTwo = 'Statement: This value remains unchanged.'
        else:
            messTwo = 'Critique: %s%s%s of %s.\n%s.' % (entry['value'],
                                                        ' is less than your previous upload for ',
                                                        entry['medal'],
                                                        medals[0][index],
                                                        'Advice: This could be an error in reading the value, so please make sure there are no sparkles covering the number in your screenshot' 
                                                        )

        await client.send_message(message.channel, '%s\n%s' % (messOne,messTwo))
                                      
    
    medalRangeName = "%s!B%s:AI%s" % (week_prefix(), user_list_index[user], user_list_index[user])
    result['values'] = medals
    result['range'] = medalRangeName
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheetId, range=medalRangeName, body=result, valueInputOption='USER_ENTERED').execute()

    rangeName = "InputLogTable!A:E"
    stuff = {'values' : [], 'range' : rangeName, 'majorDimension' : 'ROWS'}
    for entry in data:
        stuff['values'].append([message.author.id, user_names[user_list_index[user]], entry['medal'], entry['value'], message.timestamp.isoformat('T')])

    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheetId, range=rangeName, body=stuff, valueInputOption='USER_ENTERED').execute()

#creates a blank user with properly initialized values
def create_init(id):
    entry = [['=Reference!B%s' % (id)]]
    
    #hardcoded TODO
    for i in range(0,34):
        entry[0].append(1)
    
    return entry

#adds a user to the bottom of the reference sheet and the latest sheet then updates local lists
async def add_user(message):
    global service
    #check list for username
    if message.author.id in user_list_index.keys():
        await client.send_message(message.channel, 'Critique: You have already registered a username.')
        return
    
    args = message.content.split()
    if len(args) < 2:
        await client.send_message(message.channel, 'Critique: Username required.')
        return
    await client.send_message(message.channel, 'adding user %s' % (args[1]))

    spreadsheetId = '1Tsd1huHdMBcVerodjw-pHa_s4J7GP8xSHyJuL4S-6_s'
    rangeName = "Reference!A2:B"
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])
    print(len(values))
    values.append([message.author.id, args[1]])
    result['values'] = values
    rangeName = result['range']
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheetId, range=rangeName, body=result, valueInputOption='USER_ENTERED').execute()
    update_lists()
    index = user_list_index[message.author.id]
    #hardcoded value below TODO
    rangeName = "%s!A%s:AF%s" % (week_prefix(), index, index)
    request = {'range' : rangeName, 'values' : create_init(index)}
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheetId, range=rangeName, body=request, valueInputOption='USER_ENTERED').execute()
        
#changes a username in the spreadsheet on the reference sheet and latest sheet then updates local lists
async def change_user(message):
    global service
    if message.author.id not in user_list_index.keys():
        await client.send_message(message.channel, 'Critique: You have not registered a username yet.')
        return
    
    args = message.content.split()
    if len(args) < 2:
        await client.send_message(message.channel, 'Critique: Username required.')
        return
    
    if args[1] in user_names:
        await client.send_message(message.channel, 'Critique: Username taken.')
    
    index = user_list_index[message.author.id]
    await client.send_message(message.channel, 'Statement: Changing user %s to %s' % (user_names[index],args[1]))

    spreadsheetId = '1Tsd1huHdMBcVerodjw-pHa_s4J7GP8xSHyJuL4S-6_s'
    rangeName = "Reference!A%s:B%s" % (index,index)
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])
    values[0][1] = args[1]
    result['values'] = values
    rangeName = result['range']
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheetId, range=rangeName, body=result, valueInputOption='USER_ENTERED').execute()
    update_lists()

#enables the bot to start collection images: must init to a channel first
async def start_collecting(message):
    global collecting_
    collecting_ = True
    await client.send_message(message.channel, 'Statement: Image processing now active.')

#disables image collection
async def stop_collecting(message):
    global collecting_
    collecting_ = False
    await client.send_message(message.channel, 'Statement: Image processing no longer active.')

#prints whether or not the bot is accepting images
async def status_check(message):
    if collecting_:
        await client.send_message(message.channel, 'Statement: Image processing is active.')
    else:
        await client.send_message(message.channel, 'Statement: Image processing is not active.')

#right now it is not really custom
async def custom_message(message):
    await client.send_message(message.channel, 'Smug challenge: Bring it on, meatbag.')

#does not work yet TODO
async def remove_user(message):
    if message.author.id not in user_list_index.keys():
        await client.send_message(message.channel, 'Critique: You cannot unregister because you are not registered in the first place.')
        return
    
    '''requests = []
    spreadsheetId = '1Tsd1huHdMBcVerodjw-pHa_s4J7GP8xSHyJuL4S-6_s'
    index = user_list_index[message.author.id]
    # Change the spreadsheet's title
    requests.append({
        "deleteDimension": {
            "range": {
                "sheetId": 1981323919,
                "dimension": "ROWS",
                "startIndex": index,
                "endIndex": index
            }
        }
    })
    requests.append({
        "deleteDimension": {
            "range": {
                "sheetId": 1878141460,
                "dimension": "ROWS",
                "startIndex": index,
                "endIndex": index
            }
        }
    })
    # Add additional requests (operations) ... 

    body = {
        'requests': requests,
        #'valueInputOption' : 'USER_ENTERED'
    }
    response = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId,
                                                   body=body).execute()'''
    update_lists()

#prints help message
async def print_help(message):
    await client.send_message(message.channel, '%s%s%s%s%s%s' % ('?startcollection: starts image processing\n',
                                                                 '?stopcollection: stops image processing\n',
                                                                 '?register <username>: register a username for image processing\n',
                                                                 '?reregister: reregister your current username\n',
                                                                 '?status: whether or not image processing is active\n',
                                                                 '?help: this information'))

#initializes the bot to a specific discord channel
async def initialize_channel(message):
    global medal_channels_, scan_channels_
    
    args = message.content.split()
    if len(args) < 2:
        await client.send_message(message.channel, 'Critique: Channel purpose required.')
        return
    
    if message.channel.id in scan_channels_ or message.channel.id in medal_channels_ or message.channel.id in udex_channels_:
        await client.send_message(message.channel, 'Critique: Channel already initialized.')    
    elif args[1] == 'medal' and message.channel.id not in medal_channels_:
        medal_channels_.append(message.channel.id)
        await client.send_message(message.channel, 'Statement: Initialized to channel %s.' % (message.channel.id))
    elif args[1] == 'scan' and message.channel.id not in scan_channels_:
        scan_channels_.append(message.channel.id)
        await client.send_message(message.channel, 'Statement: Medal and experience leaderboard initialized to channel %s.' % (message.channel.id))
    elif args[1] == 'udex' and message.channel.id not in udex_channels_:
        udex_channels_.append(message.channel.id)
        await client.send_message(message.channel, 'Statement: Ultimate Dex initialized to channel %s.' % (message.channel.id))
    else:
        await client.send_message(message.channel, 'Critique: Channel purpose must be either "medal," "scan," or "udex."')

#updates local data lists from the reference sheet
def update_lists():
    global service, medal_list_index, user_list_index, user_names

    medal_list_index = {}
    user_list_index = {}
    user_names = ['error', 'junk']
    spreadsheetId = '1Tsd1huHdMBcVerodjw-pHa_s4J7GP8xSHyJuL4S-6_s'
    rangeName = "Reference!A2:B"
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])
    print('%s' % (result['range']))
    if not values:
        print("Error: no users found.")
        return
    else:
        index = 1
        for row in values:
            # generate user lookup index so don't have to query all the time
            #print('%s, %s' % (row[0], row[1]))
            index = index + 1
            user_names.append(row[1])
            user_list_index[row[0]] = index
    
    #hardcoded TODO
    rangeName = "Reference!C1:AJ1"
    result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])
    print('%s' % (result['range']))
    if not values:
        print("Error: no medals found.")
        return
    else:
        index = 0
        for row in values:
            # generate medal lookup index so don't have to query all the time
            for medal in row:
                #print('%s' % (medal))
                medal_list_index[medal] = index
                index = index + 1

    #TODO TEMP gather
    rangeName = "Gather!A:C"
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])
    print(len(values))
    if not values:
        print("Error: no users found.")
        return
    else:
        index = 1
        #for row in values:
            # generate user lookup index so don't have to query all the time
            #print('%s, %s' % (row[0], row[1]))
            #temp_gather_list[row[0]] = (row[1], row[2])

async def gather(message):
    global temp_gather_list
    #check list for username
    print("%s,   %s" % (message.author.id,message.author.name))
    temp_gather_list[message.author.id] = message.author.name

async def gather_update(message=None):
    global service, temp_gather_list

    spreadsheetId = '1Tsd1huHdMBcVerodjw-pHa_s4J7GP8xSHyJuL4S-6_s'
    rangeName = "Gather!A:C"
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])
    print(len(values))
    values = [[s, temp_gather_list[s][0], temp_gather_list[s][1]] for s in temp_gather_list.keys()]
    result['values'] = values
    rangeName = result['range']
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheetId, range=rangeName, body=result, valueInputOption='USER_ENTERED').execute()
    update_lists()


def main():
    global commands, client, tele_bot
    commands = {'?startcollection' : start_collecting,
                 '?stopcollection' : stop_collecting,
                 '?register' : add_user,
                 '?status' : status_check,
                 #'?unregister' : remove_user,
                 '?reregister' : change_user,
                 '?help' : print_help,
                 '?taunt' : custom_message,
                 '???init???' : initialize_channel,
                 '???gather???' : gather_update }
    
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    global service
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    update_lists()
            
    #tele_bot = telegram.Bot(token='353240955:AAHWWXcg-AOMoXbK4AUcgFBDMphn2luCV_Q')
    #tele_bot = telegram.Bot(token='343281795:AAHYQcJJU-QirfmKhx7KrIsq_PgyLkVbk-c')
    #print(tele_bot.getMe())
    #print(week_prefix())
    client.run('Mjg0NjU2OTI4MDM3MDExNDU2.C5Gy_Q.9VXU-2zeJwTeUCK_7JNButhmO_U')
    
    #gather_update()
    print("okay done now")
    
if __name__ == '__main__':
    main()
