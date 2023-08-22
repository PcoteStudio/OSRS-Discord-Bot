import logging
import nextcord
from nextcord import InvalidArgument
from nextcord.ext import commands, application_checks
from internal import utils, constants
from internal.sal.team import Team
from internal.sal import snakesandladders, salutils, salchecks
from database.sal import teamdb


class TeamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command()
    async def team(self, interaction):
        pass

    @team.subcommand(description="List all the teams participating in the current GoL session.")
    @application_checks.guild_only()
    @salchecks.game_exists()
    async def list(self, interaction: nextcord.Interaction):
        game = snakesandladders.get_game(interaction.guild.id)
        if len(game.teams) == 0:
            await interaction.send(f"{constants.EMOJI_INCORRECT} There is no team in the GoL session **{game.name}**.")
            return
        content = f"The following teams are registered to **{game.name}**:"
        for team in game.teams:
            content += f"\n- Team {salutils.format_team(team)} ({team.get_members_as_string(False, ', ')})"
        await interaction.send(content)

    @team.subcommand(description="Create a new team with the mentioned users.")
    @application_checks.guild_only()
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    @salchecks.game_exists()
    async def create(self, interaction: nextcord.Interaction, name: str, emoji: str, users: str):
        salutils.validate_team_name(name)
        salutils.validate_emoji(emoji)
        game = snakesandladders.get_game(interaction.guild.id)
        members = await utils.convert_mentions_string_into_members(interaction.guild, users)
        salutils.validate_team_users(members)

        for t in game.teams:
            for m in members:
                if t.is_in_team(m.id):
                    await interaction.send(f"{constants.EMOJI_INCORRECT} <@{m.id}> is already in team {salutils.format_team(t)}.")
                    return

        team = Team(game._id, name, emoji)
        team.add_members(members)
        game.add_team(team)
        await teamdb.insert(team)
        game.is_board_updated = False

        logging.info(
            f"{utils.format_guild_log(interaction.guild)} Team {team.name} created successfully by {interaction.user.name}.")
        await interaction.send(f"Team {salutils.format_team(team)} created successfully. Members : {team.get_members_as_string(True, ', ')}.")

    @team.subcommand(description="Add the mentioned users to the team of the mentioned member.")
    @application_checks.guild_only()
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    @salchecks.game_exists()
    async def addmembers(self, interaction: nextcord.Interaction, current_user: nextcord.User, users: str):
        game = snakesandladders.get_game(interaction.guild.id)
        team = game.get_team_by_player_id(current_user.id)
        if (not team):
            raise InvalidArgument(f"{current_user.display_name} is not a member of any team.")

        members = await utils.convert_mentions_string_into_members(interaction.guild, users)
        salutils.validate_team_users(members)

        for t in game.teams:
            if t == team:
                continue
            for m in members:
                if t.is_in_team(m.id):
                    await interaction.send(f"{constants.EMOJI_INCORRECT} <@{m.id}> is already in team {salutils.format_team(t)}.")
                    return

        team.add_members(members)
        await teamdb.update(team)

        logging.info(
            f"{utils.format_guild_log(interaction.guild)} New members successfully added to team {team.name} by {interaction.user.name}.")
        await interaction.send(f"New members successfully added to team {salutils.format_team(team)}. Members : {team.get_members_as_string(True, ', ')}.")

    @team.subcommand(description="Removed the mentioned users from their respective teams")
    @application_checks.guild_only()
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    @salchecks.game_exists()
    async def removemembers(self, interaction: nextcord.Interaction, users: str):
        game = snakesandladders.get_game(interaction.guild.id)
        members = await utils.convert_mentions_string_into_members(interaction.guild, users)
        salutils.validate_team_users(members)
        teams = []
        for m in members:
            team = game.get_team_by_player_id(m.id)
            if (not team):
                raise InvalidArgument(f"{m.display_name} is not a member of any team.")
            teams.append(team)

        for i, m in enumerate(members):
            teams[i].remove_member(m.id)
            if len(teams[i].members) == 0:
                game.remove_team(teams[i])
                await teamdb.delete(teams[i])

        await teamdb.update_many(list(set(filter(lambda t: len(t.members) > 0, teams))))

        logging.info(
            f"{utils.format_guild_log(interaction.guild)} Successfully removed members from teams by {interaction.user.name}.")
        await interaction.send(f"Members successfully removed from teams.")

    @team.subcommand(description="Delete the team the user is part of.")
    @application_checks.guild_only()
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    @salchecks.game_exists()
    async def delete(self, interaction: nextcord.Interaction, member: nextcord.Member):
        game = snakesandladders.get_game(interaction.guild.id)
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
        await interaction.send(f"The team {salutils.format_team(deleted_teams[0])} was deleted successfully.")

    @team.subcommand(description="Choose your team's emoji/pawn")
    @application_checks.guild_only()
    @salchecks.game_exists()
    @salchecks.game_has_not_started()
    @salchecks.player_is_in_team()
    @salchecks.command_is_in_team_channel()
    async def emoji(self, interaction: nextcord.Interaction, emoji: str):
        salutils.validate_emoji(emoji)
        game = snakesandladders.get_game(interaction.guild.id)
        team = game.get_team_by_player_id(interaction.user.id)
        team.emoji = emoji
        await teamdb.update(team)

        game.is_board_updated = False
        logging.info(
            f"{utils.format_guild_log(interaction.guild)} Team {team.name} emoji successfully changed by {interaction.user.name}.")
        await interaction.send(f"The team {salutils.format_team(team, False)}'s emoji was successfully changed to {team.emoji}.")

    @team.subcommand(description="Choose your team's name")
    @application_checks.guild_only()
    @salchecks.game_exists()
    @salchecks.game_has_not_started()
    @salchecks.player_is_in_team()
    @salchecks.command_is_in_team_channel()
    async def name(self, interaction: nextcord.Interaction, name: str):
        salutils.validate_team_name(name)
        game = snakesandladders.get_game(interaction.guild.id)
        team = game.get_team_by_player_id(interaction.user.id)
        previous_name = salutils.format_team(team, False)
        team.name = name
        await teamdb.update(team)

        logging.info(
            f"{utils.format_guild_log(interaction.guild)} Team {team.name} name successfully changed by {interaction.user.name}.")
        await interaction.send(f"The team {previous_name}'s name was successfully changed to {team.name}.")

    @team.subcommand(description="Choose your team's color")
    @application_checks.guild_only()
    @salchecks.game_exists()
    @salchecks.game_has_not_started()
    @salchecks.player_is_in_team()
    @salchecks.command_is_in_team_channel()
    async def color(self, interaction: nextcord.Interaction,
                    color: str = nextcord.SlashOption(name="color", choices={"Black": "black", "Blue": "blue", "Brown": "brown",
                                                                             "Crimson": "crimson", "Emerald": "emerald",
                                                                             "Fuchsia": "fuchsia", "Gray": "gray", "Indigo": "indigo",
                                                                             "Lime": "lime", "Navy blue": "navy blue", "Red": "red",
                                                                             "Turquoise": "turquoise", "White": "white"})):
        game = snakesandladders.get_game(interaction.guild.id)
        team = game.get_team_by_player_id(interaction.user.id)
        team.color = constants.COLORS[color]
        await teamdb.update(team)

        game.is_board_updated = False
        logging.info(
            f"{utils.format_guild_log(interaction.guild)} Team {team.name} color successfully changed by {interaction.user.name}.")
        await interaction.send(f"The team {salutils.format_team(team, False)}'s color was successfully changed to {color}")

    @team.error
    async def check_failure_error(self, interaction: nextcord.Interaction, error: Exception):
        if not isinstance(error, (nextcord.ApplicationCheckFailure, nextcord.ClientException)):
            raise error


def setup(bot):
    bot.add_cog(TeamCog(bot))
