import nextcord
import logging
from nextcord.ext import commands, application_checks
from internal import utils, constants
from internal.gol import gameoflife, golchecks
from database.gol import gameoflifedb, teamdb


class ChannelCog(commands.Cog):

    @nextcord.slash_command()
    async def channel(self, interaction):
        pass

    @channel.subcommand(description="Set the channel in which the bot will post team update logs.")
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    @golchecks.game_exists()
    async def logs(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel):
        game = gameoflife.get_game(interaction.guild.id)
        game.channel_logs = channel.id
        await gameoflifedb.update(game)
        await interaction.send(constants.TEXT_LOGS_CHANNEL_HAS_BEEN_SUCCESSFULLY_SET)
        logging.info(
            f"{utils.format_guild_log(interaction.guild)} GoL logs channel has been set to {channel.name} by {interaction.user.name})")

    @channel.subcommand(description="Set the channel in which the bot post the live board.")
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    @golchecks.game_exists()
    async def board(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel):
        game = gameoflife.get_game(interaction.guild.id)
        game.channel_board = channel.id
        await gameoflifedb.update(game)
        game.is_board_updated = False
        logging.info(
            f"{utils.format_guild_log(interaction.guild)} GoL live board channel has been set to {channel.name} by {interaction.user.name})")
        await interaction.send(constants.TEXT_BOARD_CHANNEL_HAS_BEEN_SUCCESSFULLY_SET)

    @channel.subcommand(description="Set the only channel in which the specified user's team can execute commands.")
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    @golchecks.game_exists()
    async def team(self, interaction: nextcord.Interaction, user: nextcord.User, channel: nextcord.TextChannel):
        game = gameoflife.get_game(interaction.guild.id)

        team = game.get_team_by_player_id(user.id)
        if team is None:
            await interaction.send(f'{constants.EMOJI_INCORRECT} {constants.TEXT_THIS_PLAYER_IS_NOT_IN_ANY_TEAM}')
            return

        team.channel = channel.id
        await teamdb.update(team)

        logging.info(
            f"{utils.format_guild_log(interaction.guild)} GoL live board channel has been set to {channel.name} by {interaction.user.name})")
        await interaction.send(constants.TEXT_TEAM_CHANNEL_HAS_BEEN_SUCCESSFULLY_SET)

    @channel.subcommand(description="Unset the current GoL channels.")
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    @golchecks.game_exists()
    async def unset(self, interaction: nextcord.Interaction):
        game = gameoflife.get_game(interaction.guild.id)
        game.channel_logs = None
        game.channel_board = None

        for team in game.teams:
            team.channel = None

        await teamdb.update_many(game.teams)
        await gameoflifedb.update(game)
        await interaction.send(constants.TEXT_SET_CHANNELS_HAVE_BEEN_SUCCESSFULLY_CLEARED)
        logging.info(
            f"{utils.format_guild_log(interaction.guild)} GoL channels have been unset by {interaction.user.name})")

    @channel.error
    async def check_failure_error(self, interaction: nextcord.Interaction, error: Exception):
        if not isinstance(error, (nextcord.ApplicationCheckFailure, nextcord.ClientException)):
            raise error


def setup(bot):
    bot.add_cog(ChannelCog(bot))
