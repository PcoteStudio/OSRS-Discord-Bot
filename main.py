import discord
import json
import os
import requests
from discord.ext import tasks

boss_display_names = ['Abyssal Sire', 'Alchemical Hydra', 'Artio', 'Barrows Chests', 'Bryophyta', 
                'Callisto', 'Calvar\'ion', 'Cerberus', 'Chambers of Xeric', 
                'Chambers of Xeric: Challenge Mode', 'Chaos Elemental', 'Chaos Fanatic', 
                'Commander Zilyana', 'Corporeal Beast', 'Crazy Archaeologist', 'Dagannoth Prime', 
                'Dagannoth Rex', 'Dagannoth Supreme', 'Deranged Archaeologist', 'General Graardor', 
                'Giant_Mole', 'Grotesque Guardians', 'Hespori', 'Kalphite Queen', 'King Black Dragon', 
                'Kraken', 'Kree\'Arra', 'K\'ril Tsutsaroth', 'Mimic', 'Nex', 'Nightmare',
                'Phosani\'s Nightmare', 'Obor', 'Phantom Muspah', 'Sarachnis', 'Scorpia', 'Skotizo',
                'Spindel', 'Tempoross', 'The Gauntlet', 'The Corrupted Gauntlet', 'Theatre of Blood',
                'Theatre of Blood: Hard Mode', 'Thermonuclear Smoke Devil', 'Tombs of Amascut',
                'Tombs of Amascut: Expert', 'TzKal-Zuk', 'TzTok-Jad', 'Venenatis', 'Vet\'ion', 'Vorkath',
                'Wintertodt', 'Zalcano', 'Zulrah']
boss_metrics = ['abyssal_sire', 'alchemical_hydra', 'artio', 'barrows_chests', 'bryophyta',
                'callisto', 'calvarion', 'cerberus', 'chambers_of_xeric', 
                'chambers_of_xeric_challenge_mode', 'chaos_elemental', 'chaos_fanatic',
                'commander_zilyana', 'corporeal_beast', 'crazy_archaeologist', 'dagannoth_prime',
                'dagannoth_rex', 'dagannoth_supreme', 'deranged_archaeologist', 'general_graardor', 
                'giant_mole', 'grotesque_guardians', 'hespori', 'kalphite_queen', 'king_black_dragon',
                'kraken', 'kreearra', 'kril_tsutsaroth', 'mimic', 'nex', 'nightmare',
                'phosanis_nightmare', 'obor', 'phantom_muspah', 'sarachnis', 'scorpia', 'skotizo',
                'spindel', 'tempoross', 'the_gauntlet', 'the_corrupted_gauntlet', 'theatre_of_blood',
                'theatre_of_blood_hard_mode', 'thermonuclear_smoke_devil', 'tombs_of_amascut',
                'tombs_of_amascut_expert', 'tzkal_zuk', 'tztok_jad', 'venenatis', 'vetion', 'vorkath',
                'wintertodt', 'zalcano', 'zulrah']

def read_secrets() -> dict:
    filename = os.path.join('secrets.json')
    try:
        with open(filename, mode='r') as f:
            return json.loads(f.read())
    except FileNotFoundError:
        return {}
secrets = read_secrets()

def getBossHiscore(boss_metric : str):
    response = requests.get(
        f"https://api.wiseoldman.net/v2/groups/{secrets['WOM_GROUP']}/hiscores?metric={boss_metric}",
        headers={"x-api-key": secrets['WOM_API_KEY']})
    boss_hiscore = json.loads(response.text)
    return boss_hiscore

def findTopX(boss_hiscore : json, x : int):
    topX = []
    for entry in boss_hiscore:
        player, data = entry['player'], entry['data']
        topX.append({ 'displayName': player['displayName'], 
                     'kills': "{:,}".format(data['kills']).replace(",", " ") })
        if(len(topX) >= x):
            break
    return topX

def getAllBossesTopX(x : int):
    bosses_topX = []
    for i, metric in enumerate(boss_metrics):
        boss_hiscore = getBossHiscore(metric)
        topX = findTopX(boss_hiscore, x)
        bosses_topX.append({ 'displayName': boss_display_names[i], 'topX': topX })
    return bosses_topX

def formatBossesTopX(all_bosses_topX : list):
    post = "**Boss Killcounts**"
    for boss in all_bosses_topX:
        post += f"\n{boss['displayName']}```"
        for i, data in enumerate(boss['topX']):
            post += f"\n{i+1}. {data['displayName']}: {data['kills']}"
        post += " ```"
    return post

# Bot invite link https://discord.com/api/oauth2/authorize?client_id=1100974700949159986&permissions=2419452944&scope=bot

class BotClient(discord.Client):
    @tasks.loop(minutes=secrets['UPDATE_HS_EVERY_X_MIN'])
    async def update_hs_channel(self):
        print("Updating HS")
        try:
            channel = client.get_channel(secrets['HS_CHANNEL_ID'])
            botMsgs = []
            async for msg in channel.history():
                if (msg.author.id == client.user.id): botMsgs.insert(0, msg)
            content = formatBossesTopX(getAllBossesTopX(3))
            parts = content.split(" ```\n")
            content = []
            for part in parts:
                if(len(content) == 0 or len(content[len(content)-1]) > 1600):
                    content.append(part + " ```\n")
                else:
                    content[len(content)-1] += part + " ```\n"
            content[len(content)-1] = content[len(content)-1][:-4]
            
            i = 0
            for msg in botMsgs:
                if(i >= len(content)): await msg.delete()
                else: await msg.edit(content=content[i])
                i += 1
            
            for j in range(i, len(content)):
                await channel.send(content[j])
            print("Updated HS")
        except Exception as e:
            print(f"An error occurred while updating HS: {str(e)}")
    
    async def on_ready(self): 
        print(f'Logged in as {self.user}!')
        self.update_hs_channel.start()

intents = discord.Intents.default()
intents.message_content = True

client = BotClient(intents=intents)
client.run(secrets['BOT_TOKEN'])