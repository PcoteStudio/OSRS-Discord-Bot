import nextcord as discord
from internal.hiscores import Hiscores
from nextcord.ext import commands, tasks
from internal import confirmation, constants
import logging


class CogHiscores(commands.Cog):
    started_tasks = []

    def __init__(self, bot):
        from internal import configmanager
        self.bot = bot
        self.hiscores = []
        config = configmanager.instance
        hs_config = config.get('HISCORES')
        for entry in hs_config:
            self.hiscores.append(Hiscores(config.get('WOM_API_KEY'),
                                          entry['wom_group'],
                                          entry['discord_channel'],
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
            botMsgs = []
            async for msg in channel.history():
                if (msg.author.id == self.bot.user.id):
                    botMsgs.insert(0, msg)
            content = await hs.getUpdatedHiscoresToPost(1600)

            i = 0
            for msg in botMsgs:
                if (i >= len(content)):
                    await msg.delete()
                else:
                    await msg.edit(content=content[i])
                i += 1

            for j in range(i, len(content)):
                await channel.send(content[j])

            logging.info(f"Updated HS for {hs.server_name}.")
        except Exception as e:
            logging.error(f"An error occurred while updating HS for {hs.server_name}: {str(e)}")

    @commands.Cog.listener()
    async def on_ready(self):
        if (len(self.started_tasks) == 0):
            for hs in self.hiscores:
                t = tasks.loop(minutes=hs.update_frequency_min)(self.update_hs_channel)
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
                return
        await ctx.message.add_reaction(constants.EMOJI_CANCEL)


def setup(bot):
    bot.add_cog(CogHiscores(bot))
