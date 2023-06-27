import nextcord
from nextcord.ext import commands
from internal import constants


class DeveloperCog(commands.Cog):

    @commands.command()
    @commands.is_owner()
    async def ping(self, ctx):
        await ctx.send("Pong")

    @nextcord.slash_command()
    async def help(self, interaction):
        content = "**Available commands**"
        content += "```"
        content += "\nGame commands"
        content += "\n  /help               \tDisplays the list of commands"
        content += "\n  /stats              \tDisplays every team's statistics"
        content += "\n  /stats <user>       \tDisplays the player's team statistics"
        content += "\n  /team list          \tDisplays a list of every team and their members"
        content += "\nTeam commands (before event)"
        content += "\n  /team name <name>   \tSets your team's name"
        content += "\n  /team emoji <emoji> \tSets your team's emoji"
        content += "\n  /team color <color> \tSets your team's color on the board"
        content += "\nTeam commands (during event)"
        content += "\n  /current            \tDisplay the team's current grind"
        content += "\n  /roll               \tRoll the team's next grind"
        content += "\n```"
        await interaction.send(content)


def setup(bot):
    bot.add_cog(DeveloperCog(bot))
