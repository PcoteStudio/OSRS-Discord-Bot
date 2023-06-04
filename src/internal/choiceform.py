import nextcord
import asyncio
from nextcord.ext import commands
from internal.bot import Bot


async def slash_choose(bot: Bot, interaction: nextcord.Interaction, emojis: list, authorized_ids: list = []):
    message = await interaction.original_message()

    def check(r, u):
        return str(r.emoji) in emojis and r.message.id == message.id and (u.id == interaction.user.id or u.id in authorized_ids)

    for e in emojis:
        await message.add_reaction(e)

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=300.0, check=check)
            emoji = str(reaction.emoji)
            if emoji not in emojis:
                continue
            i = emojis.index(emoji)
            await message.clear_reactions()
            return i
        except asyncio.TimeoutError:
            await message.clear_reactions()
            return None


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
            await message.clear_reactions()
            return i
        except asyncio.TimeoutError:
            return None
