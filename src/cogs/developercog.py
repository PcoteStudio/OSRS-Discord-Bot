from nextcord.ext import commands


class DeveloperCog(commands.Cog):

    @commands.command()
    @commands.is_owner()
    async def ping(self, ctx):
        await ctx.send("Pong")


def setup(bot):
    bot.add_cog(DeveloperCog(bot))
