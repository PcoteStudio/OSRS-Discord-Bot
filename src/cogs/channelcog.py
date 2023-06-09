import nextcord
import logging
from nextcord.ext import commands, application_checks
from internal import utils, constants
from internal.gol import gameoflife, golutils
from database import gameoflifedb


class ChannelCog(commands.Cog):

    @nextcord.slash_command(guild_ids=constants.COMMANDS_GUILD_ID)
    async def channel(self, interaction):
        pass

    @channel.subcommand(description="Set the channel in which the bot will post team update logs.")
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    async def logs(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel):
        game = gameoflife.get_game(interaction.guild.id)
        if game is None:
            await interaction.send(f"{constants.EMOJI_INCORRECT} {constants.TEXT_NO_ACTIVE_GOL_SESSION_ON_SERVER}")
            return
        game.channel_logs = channel.id
        await gameoflifedb.update(game)
        await interaction.send(constants.TEXT_LOGS_CHANNEL_HAS_BEEN_SUCCESSFULLY_SET)
        logging.info(
            f"{utils.format_guild_log(interaction.guild)} GoL logs channel has been set to {channel.name} by {interaction.user.name})")

    @channel.subcommand(description="Set the channel in which the bot post the live board.")
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    async def board(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel):
        game = gameoflife.get_game(interaction.guild.id)
        if game is None:
            await interaction.send(f"{constants.EMOJI_INCORRECT} {constants.TEXT_NO_ACTIVE_GOL_SESSION_ON_SERVER}")
            return
        game.channel_board = channel.id
        await gameoflifedb.update(game)
        game.is_board_updated = False
        logging.info(
            f"{utils.format_guild_log(interaction.guild)} GoL live board channel has been set to {channel.name} by {interaction.user.name})")
        await interaction.send(constants.TEXT_BOARD_CHANNEL_HAS_BEEN_SUCCESSFULLY_SET)

    @channel.subcommand(description="Unset the current GoL channels.")
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
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
            f"{utils.format_guild_log(interaction.guild)} GoL channels have been unset by {interaction.user.name})")

    @channel.error
    async def check_failure_error(self, interaction: nextcord.Interaction, error: Exception):
        if not isinstance(error, nextcord.ApplicationCheckFailure):
            raise error


def setup(bot):
    bot.add_cog(ChannelCog(bot))
