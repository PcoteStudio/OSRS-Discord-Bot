import aiohttp
from internal import constants


class Hiscores():
    def __init__(self, WOM_API_KEY: str, wom_group: int, channel_id: int,
                 displayed_top_x: int, update_frequency_min: int, server_name: str,
                 display_boss: bool, display_clue: bool, display_activity: bool):
        self.WOM_API_KEY = WOM_API_KEY
        self.wom_group = wom_group
        self.channel_id = channel_id
        self.update_frequency_min = update_frequency_min
        self.server_name = server_name
        self.displayed_top_x = displayed_top_x
        self.display_boss = display_boss
        self.display_clue = display_clue
        self.display_activity = display_activity

    async def getHiscore(self, metric: str, top_x: int):
        async with aiohttp.ClientSession(headers={"x-api-key": self.WOM_API_KEY}) as session:
            async with session.get(f"https://api.wiseoldman.net/v2/groups/{self.wom_group}/hiscores?metric={metric}&limit={top_x}") as resp:
                boss_hiscore = await resp.json()
                return boss_hiscore

    def findTopX(self, hiscore: list, x: int):
        topX = []
        for entry in hiscore:
            player, data = entry['player'], entry['data']
            topX.append({'displayName': player['displayName'],
                        'kills': "{:,}".format(data['kills' if ('kills') in data else 'score']).replace(",", " ")})
            if (len(topX) >= x):
                break
        return topX

    async def getTopXFromMetrics(self, metrics: list, names: list, x: int):
        if (metrics == 'league_points'):
            x = 10
        metric_top_x = []
        for i, metric in enumerate(metrics):
            hiscore = await self.getHiscore(metric, self.displayed_top_x)
            topX = self.findTopX(hiscore, x)
            metric_top_x.append({'displayName': names[i], 'topX': topX})
        return metric_top_x

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

    def formatBosses(self, all_bosses_top_x: list, all_clues_top_x: list, all_activities_top_x: list):
        if self.displayed_top_x == 1:
            return self.formatBossesTop1(all_bosses_top_x, all_clues_top_x, all_activities_top_x)
        if self.displayed_top_x >= 1:
            return self.formatBossesTopX(all_bosses_top_x, all_clues_top_x, all_activities_top_x)
        else:
            return ""

    def formatBossesTop1(self, all_bosses_top1: list, all_clues_top1: list, all_activities_top1: list):
        post = "**Boss Killcounts**"
        for boss in all_bosses_top1:
            post += f"\n{boss['displayName']}: {boss['topX'][0]['displayName']} - {boss['topX'][0]['kills']}"
        post += "\n**Clue Completions**"
        for clue in all_clues_top1:
            post += f"\n{clue['displayName']}: {clue['topX'][0]['displayName']} - {clue['topX'][0]['kills']}"
        post += "\n**Other Activities**"
        for act in all_activities_top1:
            post += f"\n{act['displayName']}: {act['topX'][0]['displayName']} - {act['topX'][0]['kills']}"
        return post

    def formatBossesTopX(self, all_bosses_top_x: list, all_clues_top_x: list, all_activities_top_x: list):
        post = ""
        if self.display_boss:
            post += "**Boss Killcounts**\n"
            for boss in all_bosses_top_x:
                post += f"{boss['displayName']}```"
                for i, data in enumerate(boss['topX']):
                    post += f"\n{i+1}. {data['displayName']}: {data['kills']}"
                post += " ```\n"
        if self.display_clue:
            post += "**Clue Completions**\n"
            for clue in all_clues_top_x:
                post += f"{clue['displayName']}```"
                for i, data in enumerate(clue['topX']):
                    post += f"\n{i+1}. {data['displayName']}: {data['kills']}"
                post += " ```\n"
        if self.display_activity:
            post += "**Other Activities**\n"
            for act in all_activities_top_x:
                post += f"{act['displayName']}```"
                for i, data in enumerate(act['topX']):
                    post += f"\n{i+1}. {data['displayName']}: {data['kills']}"
                post += " ```\n"
        return post

    async def getUpdatedHiscoresToPost(self, split_length):
        bosses_top_x = [] if (self.display_boss == False) else await self.getTopXFromMetrics(constants.BOSS_METRICS, constants.BOSS_DISPLAY_NAMES, self.displayed_top_x)
        clues_top_x = [] if (self.display_clue == False) else await self.getTopXFromMetrics(constants.CLUE_METRICS, constants.CLUE_DISPLAY_NAMES, self.displayed_top_x)
        activities_top_x = [] if (self.display_activity == False) else await self.getTopXFromMetrics(
            constants.ACTIVITY_METRICS, constants.ACTIVITY_DISPLAY_NAMES, self.displayed_top_x)
        content = self.formatBosses(bosses_top_x, clues_top_x, activities_top_x)
        content = self.splitContentInMessages(content, split_length)
        return content
