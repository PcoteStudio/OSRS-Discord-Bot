import random
import nextcord
from nextcord.ext import commands
from internal import constants, choiceform


class CogGameOfLife(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roll")
    @commands.bot_has_permissions(add_reactions=True)
    async def roll(self, ctx):
        n = random.randrange(1, 11)
        content = f'{constants.EMOJI_DICE} <@{ctx.message.author.id}> rolled a {n}!'
        content += "\nYou path is branching. You will have to choose which branch to take to continue..."
        content += f"\n{constants.EMOJI_LEFT_ARROW} Choose left to do **ABC**."
        content += f"\n{constants.EMOJI_RIGHT_ARROW} Choose right to do **XYZ**."
        content += f"\nReact with to this message with your choice."
        msg = await ctx.send(content)
        choice = await choiceform.choose(ctx, msg, [constants.EMOJI_LEFT_ARROW, constants.EMOJI_RIGHT_ARROW])
        if choice == 0:
            await ctx.send(f"<@{ctx.message.author.id}> has chosen the left path. Do **ABC** to progress and be able to roll again.")
        if choice == 1:
            await ctx.send(f"<@{ctx.message.author.id}> has chosen the right path. Do **XYZ** to progress and be able to roll again.")


def setup(bot):
    bot.add_cog(CogGameOfLife(bot))
