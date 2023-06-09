import logging
import nextcord
from nextcord.ext import commands, application_checks
from internal import utils, constants
from internal.gol.team import Team
from internal.gol import gameoflife, golutils, golchecks
from database import teamdb


class TeamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(guild_ids=constants.COMMANDS_GUILD_ID)
    async def team(self, interaction):
        pass

    @team.subcommand(description="List all the teams participating in the current GoL session.")
    @application_checks.guild_only()
    @golchecks.game_exists()
    async def list(self, interaction: nextcord.Interaction):
        game = gameoflife.get_game(interaction.guild.id)
        if len(game.teams) == 0:
            await interaction.send(f"{constants.EMOJI_INCORRECT} There is no team in the GoL session **{game.name}**.")
            return
        content = f"The following teams are registered to **{game.name}**:"
        for team in game.teams:
            content += f"\n- Team {golutils.format_team(team)} ({team.get_members_as_string(False, ' ')})"
        await interaction.send(content)

    @team.subcommand(description="Create a new team with the mentioned users.")
    @application_checks.guild_only()
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    @golchecks.game_exists()
    async def create(self, interaction: nextcord.Interaction, name: str, emoji: str, users: str):
        game = gameoflife.get_game(interaction.guild.id)
        members = await utils.convert_mentions_string_into_members(interaction.guild, users)

        if len(members) == 0:
            await interaction.send(f"{constants.EMOJI_INCORRECT} A team needs at least 1 member.")
            return

        for t in game.teams:
            for m in members:
                if t.is_in_team(m.id):
                    await interaction.send(f"{constants.EMOJI_INCORRECT} <@{m.id}> is already in team {golutils.format_team(t)}.")
                    return

        team = Team(game._id, name, emoji)
        team.add_members(members)
        game.add_team(team)
        await teamdb.insert(team)
        game.is_board_updated = False

        logging.info(
            f"{utils.format_guild_log(interaction.guild)} Team {team.name} created successfully by {interaction.user.name}.")
        await interaction.send(f"Team {golutils.format_team(team)} created successfully. Members : {team.get_members_as_string(True, ' ')}.")

    @team.subcommand(description="Delete the team the user is part of.")
    @application_checks.guild_only()
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    @golchecks.game_exists()
    async def delete(self, interaction: nextcord.Interaction, member: nextcord.Member):
        game = gameoflife.get_game(interaction.guild.id)
        if len(game.teams) == 0:
            await interaction.send(f'{constants.EMOJI_INCORRECT} There is no team on this server.')
            return

        deleted_teams = []
        for t in game.teams:
            if t.is_in_team(member.id):
                deleted_teams.append(t)

        for t in deleted_teams:
            game.remove_team(t)
            await teamdb.delete(t)

        if len(deleted_teams) == 0:
            await interaction.send(f"{constants.EMOJI_INCORRECT} <@{member.id}> isn't in any team.")
            return

        game.is_board_updated = False
        logging.info(
            f"{utils.format_guild_log(interaction.guild)} Team {deleted_teams[0].name} deleted successfully by {interaction.user.name}.")
        await interaction.send(f"The team {golutils.format_team(deleted_teams[0])} was deleted successfully.")

    @team.error
    async def check_failure_error(self, interaction: nextcord.Interaction, error: Exception):
        if not isinstance(error, nextcord.ApplicationCheckFailure):
            raise error


def setup(bot):
    bot.add_cog(TeamCog(bot))
