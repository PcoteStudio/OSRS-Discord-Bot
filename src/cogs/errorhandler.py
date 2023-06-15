import nextcord
import logging
from nextcord.ext import commands
from internal import constants


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: nextcord.Interaction, error):
        if not isinstance(error, (nextcord.ApplicationCheckFailure, nextcord.ClientException)):
            logging.error(error)
        await interaction.send(f"{constants.EMOJI_INCORRECT} {(str(error.original if hasattr(error, 'original') else error)).capitalize()}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if not isinstance(error, (nextcord.ApplicationCheckFailure, nextcord.ClientException)):
            logging.error(error)
        await ctx.send(f"{constants.EMOJI_INCORRECT} {(str(error.original if hasattr(error, 'original') else error)).capitalize()}")


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
