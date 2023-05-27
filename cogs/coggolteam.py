import nextcord
from nextcord.ext import commands, application_checks
from internal import constants, utils
from internal.gol.team import Team


class CogGolTeam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_gol_admin():
        def predicate(interaction: nextcord.Interaction):
            return True  # Until implemented
        return application_checks.check(predicate)

    @nextcord.slash_command(guild_ids=[933103168374583417])
    async def team(self, interaction):
        role = nextcord.utils.get(interaction.guild.roles, name="Wololo")
        if role not in interaction.user.roles:
            await interaction.send(f'{constants.EMOJI_CANCEL} You do not have the rights to use this command.')
            return

        await interaction.send('You have the rights to use this command')

    @is_gol_admin()
    @team.subcommand()
    async def create(self, interaction: nextcord.Interaction, name: str, emoji: str, users: str):
        team = Team(name, emoji, await utils.convert_mentions_string_into_members(interaction.guild, users))

        content = f"Team **{name}** {emoji} created successfully."
        if len(team.members) > 0:
            content += f" Members : {team.get_members_as_string(' ')}"
        await interaction.send(content)


def setup(bot):
    bot.add_cog(CogGolTeam(bot))
