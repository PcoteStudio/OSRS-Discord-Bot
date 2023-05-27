import aiohttp
from internal import constants


class Hiscores():
    def __init__(self, wom_api_key: str, wom_group: int, channel_id: int, update_frequency_min: int, displayed_top_x: int, server_name: str):
        self.wom_api_key = wom_api_key
        self.wom_group = wom_group
        self.channel_id = channel_id
        self.update_frequency_min = update_frequency_min
        self.server_name = server_name
        self.displayed_top_x = displayed_top_x

    async def getBossHiscore(self, boss_metric: str):
        async with aiohttp.ClientSession(headers={"x-api-key": self.wom_api_key}) as session:
            async with session.get(f"https://api.wiseoldman.net/v2/groups/{self.wom_group}/hiscores?metric={boss_metric}") as resp:
                boss_hiscore = await resp.json()
                return boss_hiscore

    def findTopX(self, boss_hiscore: list, x: int):
        topX = []
        for entry in boss_hiscore:
            player, data = entry['player'], entry['data']
            topX.append({'displayName': player['displayName'], 'kills': "{:,}".format(
                data['kills']).replace(",", " ")})
            if (len(topX) >= x):
                break
        return topX

    async def getAllBossesTopX(self, x: int):
        bosses_topX = []
        for i, metric in enumerate(constants.BOSS_METRICS):
            boss_hiscore = await self.getBossHiscore(metric)
            topX = self.findTopX(boss_hiscore, x)
            bosses_topX.append(
                {'displayName': constants.BOSS_DISPLAY_NAMES[i], 'topX': topX})
        return bosses_topX

    def splitContentInMessages(self, content, split_length):
        parts = content.split(" ```\n")
        content = []
        for part in parts:
            if (len(content) == 0 or len(content[len(content)-1]) > split_length):
                content.append(part + " ```\n")
            else:
                content[len(content)-1] += part + " ```\n"
        content[len(content)-1] = content[len(content)-1][:-4]
        return content

    def formatBosses(self, topX):
        if self.displayed_top_x == 1:
            return self.formatBossesTop1(topX)
        if self.displayed_top_x >= 1:
            return self.formatBossesTopX(topX)
        else:
            return ""

    def formatBossesTop1(self, all_bosses_top1: list):
        post = "**Boss Killcounts**"
        for boss in all_bosses_top1:
            post += f"\n{boss['displayName']}: {boss['topX'][0]['displayName']} - {boss['topX'][0]['kills']}"
        return post

    def formatBossesTopX(self, all_bosses_topX: list):
        post = "**Boss Killcounts**"
        for boss in all_bosses_topX:
            post += f"\n{boss['displayName']}```"
            for i, data in enumerate(boss['topX']):
                post += f"\n{i+1}. {data['displayName']}: {data['kills']}"
            post += " ```"
        return post
