import nextcord as discord
import asyncio
from nextcord.ext import commands
from internal import constants


async def confirm(ctx: commands.Context, message: discord.Message):

    def check(r, u):
        return str(r.emoji) in (constants.EMOJI_CONFIRM, constants.EMOJI_CANCEL) and u.id == ctx.author.id and r.message.id == message.id

    await message.add_reaction(constants.EMOJI_CONFIRM)
    await message.add_reaction(constants.EMOJI_CANCEL)

    try:
        reaction, user = await ctx.bot.wait_for('reaction_add', timeout=120.0, check=check)
        emoji = str(reaction.emoji)
        if emoji == constants.EMOJI_CONFIRM:
            return True
        return False

    except asyncio.TimeoutError:
        return None
