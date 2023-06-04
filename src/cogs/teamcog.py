import logging
import nextcord
from nextcord.ext import commands
from internal import utils
from internal.gol.team import Team
from internal.gol import gameoflife, golutils
from database import teamdb


class TeamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @utils.is_in_guild()
    @nextcord.slash_command(guild_ids=[1114607456304246784])
    async def team(self, interaction):
        pass

    @team.subcommand()
    async def list(self, interaction: nextcord.Interaction):
        game = gameoflife.get_game(interaction.guild.id)
        if game is None:
            await interaction.send(f":x: There is no active GoL session on this server.")
            return
        if len(game.teams) == 0:
            await interaction.send(f":x: There is no team in the GoL session **{game.name}**.")
            return
        content = f"The following teams are registered to **{game.name}**:"
        for team in game.teams:
            content += f"\n- Team {golutils.format_team(team)} ({team.get_members_as_string(False, ' ')})"
        await interaction.send(content)

    @utils.is_gol_admin()
    @team.subcommand(description="Create a new team with the mentioned users.")
    async def create(self, interaction: nextcord.Interaction, name: str, emoji: str, users: str):
        game = gameoflife.get_game(interaction.guild.id)
        if game is None:
            await interaction.send(f':x: There is no active GoL session on this server to add a team to.')
            return

        members = await utils.convert_mentions_string_into_members(interaction.guild, users)

        if len(members) == 0:
            await interaction.send(f":x: A team can't be empty.")
            return

        for t in game.teams:
            for m in members:
                if t.is_in_team(m.id):
                    await interaction.send(f":x: <@{m.id}> is already in team {golutils.format_team(t)}.")
                    return

        team = Team(game._id, name, emoji)
        team.add_members(members)
        game.add_team(team)
        await teamdb.insert(team)

        content = f"Team **{name}** {emoji} created successfully. Members : {team.get_members_as_string(True, ' ')}."
        await interaction.send(content)

    @utils.is_gol_admin()
    @team.subcommand(description="Delete the team the user is part of.")
    async def delete(self, interaction: nextcord.Interaction, member: nextcord.Member):
        game = gameoflife.get_game(interaction.guild.id)
        if game is None or len(game.teams) == 0:
            await interaction.send(f':x: There is no team on this server.')
            return

        deleted_teams = []
        for t in game.teams:
            if t.is_in_team(member.id):
                deleted_teams.append(t)

        for t in deleted_teams:
            game.remove_team(t)
            await teamdb.delete(t)

        if len(deleted_teams) == 0:
            await interaction.send(f":x: <@{member.id}> isn't in any team.")
            return

        await interaction.send(f"The team {golutils.format_team(deleted_teams[0])} was deleted successfully.")


def setup(bot):
    bot.add_cog(TeamCog(bot))
