import nextcord
from nextcord.ext import commands
from internal import constants, utils
from internal.gol.team import Team


class TeamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(guild_ids=[933103168374583417])
    async def team(self, interaction):
        pass

    @team.subcommand()
    @utils.is_gol_admin()
    async def create(self, interaction: nextcord.Interaction, name: str, emoji: str, users: str):
        team = Team(name, emoji, await utils.convert_mentions_string_into_members(interaction.guild, users))

        content = f"Team **{name}** {emoji} created successfully."
        if len(team.members) > 0:
            content += f" Members : {team.get_members_as_string(' ')}"
        await interaction.send(content)


def setup(bot):
    bot.add_cog(TeamCog(bot))
