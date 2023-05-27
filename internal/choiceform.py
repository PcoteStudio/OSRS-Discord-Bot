import nextcord
import asyncio
from nextcord.ext import commands


async def choose(ctx: commands.Context, message: nextcord.Message, emojis: list):

    def check(r, u):
        return str(r.emoji) in emojis and u.id == ctx.author.id and r.message.id == message.id

    for e in emojis:
        await message.add_reaction(e)

    while True:
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=120.0, check=check)
            emoji = str(reaction.emoji)
            if emoji not in emojis:
                continue
            i = emojis.index(emoji)
            return i
        except asyncio.TimeoutError:
            return None
