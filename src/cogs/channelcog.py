import nextcord
import logging
from nextcord.ext import commands
from internal import utils, constants
from internal.gol import gameoflife
from database import gameoflifedb


class ChannelCog(commands.Cog):

    @utils.is_in_guild()
    @nextcord.slash_command(guild_ids=[1114607456304246784])
    async def channel(self, interaction):
        pass

    @utils.is_gol_admin()
    @channel.subcommand(description="Set the channel in which the bot will post team update logs.")
    async def logs(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel):
        game = gameoflife.get_game(interaction.guild.id)
        if game is None:
            await interaction.send(f"{constants.EMOJI_INCORRECT} {constants.TEXT_NO_ACTIVE_GOL_SESSION_ON_SERVER}")
            return
        game.channel_logs = channel.id
        await gameoflifedb.update(game)
        await interaction.send(constants.TEXT_LOGS_CHANNEL_HAS_BEEN_SUCCESSFULLY_SET)
        logging.info(
            f"GoL logs channel has been set (channel_name:{channel.name}, channel_id:{channel.id})")

    @utils.is_gol_admin()
    @channel.subcommand(description="Set the channel in which the bot post the live board.")
    async def board(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel):
        game = gameoflife.get_game(interaction.guild.id)
        if game is None:
            await interaction.send(f"{constants.EMOJI_INCORRECT} {constants.TEXT_NO_ACTIVE_GOL_SESSION_ON_SERVER}")
            return
        game.channel_board = channel.id
        await gameoflifedb.update(game)
        await interaction.send(constants.TEXT_BOARD_CHANNEL_HAS_BEEN_SUCCESSFULLY_SET)
        logging.info(
            f"GoL live board channel has been set (channel_name:{channel.name}, channel_id:{channel.id})")

    @utils.is_gol_admin()
    @channel.subcommand(description="Unset the current GoL channels.")
    async def unset(self, interaction: nextcord.Interaction):
        game = gameoflife.get_game(interaction.guild.id)
        if game is None:
            await interaction.send(f"{constants.EMOJI_INCORRECT} {constants.TEXT_NO_ACTIVE_GOL_SESSION_ON_SERVER}")
            return
        game.channel_logs = None
        game.channel_board = None
        await gameoflifedb.update(game)
        await interaction.send(constants.TEXT_SET_CHANNELS_HAVE_BEEN_SUCCESSFULLY_CLEARED)
        logging.info(
            f"GoL channels have been unset (game_name:{game.name}, game_id:{game._id})")


def setup(bot):
    bot.add_cog(ChannelCog(bot))
