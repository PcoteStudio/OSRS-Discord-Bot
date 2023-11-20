import sys
import traceback
from internal.hiscores import Hiscores
from nextcord.ext import commands, tasks
from internal import constants
import logging


class HiscoresCog(commands.Cog):
    started_tasks = []

    def __init__(self, bot):
        from internal import configmanager
        self.bot = bot
        self.hiscores = []
        config = configmanager.instance
        hs_config = config.get('HISCORES')
        for entry in hs_config:
            if entry['enabled'] == False:
                continue
            if entry.get('discord_league_channel') == None:
                entry['discord_league_channel'] = None
            self.hiscores.append(Hiscores(config.get('WOM_API_KEY'),
                                          entry['wom_group'],
                                          entry['discord_channel'],
                                          entry['discord_league_channel'],
                                          entry['displayed_top_x'],
                                          entry['update_frequency_min'],
                                          entry['server_name'],
                                          entry['display_boss'],
                                          entry['display_clue'],
                                          entry['display_activity']))

    async def update_hs_channel(self, hs):
        logging.info(f"Updating HS for {hs.server_name}...")
        try:
            channel = self.bot.get_channel(hs.channel_id)
            botMsgs = [msg async for msg in channel.history() if msg.author.id == self.bot.user.id]
            content = await hs.getUpdatedHiscoresToPost(1600)

            i = 0
            for msg in reversed(botMsgs):
                if (i >= len(content)):
                    await msg.delete()
                else:
                    await msg.edit(content=content[i])
                i += 1

            for j in range(i, len(content)):
                await channel.send(content[j])

            logging.info(f"Updated HS for {hs.server_name}.")
        except Exception as e:
            logging.error(
                f"An error occurred while updating HS for {hs.server_name}: {str(e)}")
            traceback.print_exception(*sys.exc_info())

    async def update_league_hs_channel(self, hs):
        try:
            if not hs.league_channel_id:
                return

            logging.info(f"Updating League HS for {hs.server_name}...")
            channel = self.bot.get_channel(hs.league_channel_id)
            botMsgs = [msg async for msg in channel.history() if msg.author.id == self.bot.user.id]
            content = [await hs.getUpdatedLeagueHiscoresToPost()]

            i = 0
            for msg in reversed(botMsgs):
                if (i >= len(content)):
                    await msg.delete()
                else:
                    await msg.edit(content=content[i])
                i += 1

            for j in range(i, len(content)):
                await channel.send(content[j])

            logging.info(f"Updated League HS for {hs.server_name}.")
        except Exception as e:
            logging.error(
                f"An error occurred while updating League HS for {hs.server_name}: {str(e)}")
            traceback.print_exception(*sys.exc_info())

    @commands.Cog.listener()
    async def on_ready(self):
        if (len(self.started_tasks) == 0):
            for hs in self.hiscores:
                tl = tasks.loop(minutes=hs.update_frequency_min /
                                3)(self.update_league_hs_channel)
                self.started_tasks.append(tl)
                tl.start(hs)
                t = tasks.loop(minutes=hs.update_frequency_min)(
                    self.update_hs_channel)
                self.started_tasks.append(t)
                t.start(hs)

    @commands.command()
    @commands.is_owner()
    async def refresh(self, ctx):
        for hs in self.hiscores:
            if (hs.channel_id == ctx.channel.id):
                await ctx.message.add_reaction(constants.EMOJI_LOADING)
                await self.update_hs_channel(hs)
                await ctx.message.delete()


def setup(bot):
    bot.add_cog(HiscoresCog(bot))
