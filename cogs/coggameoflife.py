import random
import nextcord as discord
from nextcord.ext import commands


class CogGameOfLife(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roll")
    @commands.bot_has_permissions(add_reactions=True)
    async def roll(self, ctx):
        n = random.randrange(1, 11)
        msg = await ctx.send(f'<@{ctx.message.author.id}> rolled a {n}!')


def setup(bot):
    bot.add_cog(CogGameOfLife(bot))
