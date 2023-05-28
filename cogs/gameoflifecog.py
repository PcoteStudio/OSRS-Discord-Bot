import random
import nextcord
from nextcord.ext import commands
from internal import constants, choiceform, utils
from internal.gol import gameoflife
from internal.gol.gameoflife import GameOfLife
from database import gameoflifedb, tilenodedb


class GameOfLifeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(guild_ids=[933103168374583417])
    async def gol(self, interaction):
        pass

    @gol.subcommand()
    @utils.is_in_guild()
    @utils.is_gol_admin()
    async def create(self, interaction: nextcord.Interaction, name: str):
        game_was_archived = False
        game = None if interaction.guild.id not in gameoflife.games else gameoflife.games[
            interaction.guild.id]
        if game is not None:
            await interaction.send(f'A GoL session already exists for this server. Do you wish to overwrite **{game.name}**?')
            choice = await choiceform.slash_choose(self.bot, interaction, [constants.EMOJI_CONFIRM, constants.EMOJI_CANCEL])
            if choice == None:
                await interaction.edit_original_message(content='The GoL session creation has been canceled after no reaction from the user.')
                return
            elif choice == 1:
                await interaction.edit_original_message(content='The GoL session creation has been canceled by the user.')
                return
            else:
                await gameoflifedb.archive(game)
                gameoflife.games[game.guild_id] = None
                await interaction.edit_original_message(content=f'The existing GoL session **{game.name}** has been archived.')
                game_was_archived = True

        game = GameOfLife(interaction.guild.id, name)
        await game.generate_board()
        await gameoflifedb.insert(game)
        await tilenodedb.insert_many(game.tiles)
        gameoflife.games[game.guild_id] = game
        content = f"A GoL session **{name}** was successfully created for this server."
        if game_was_archived:
            await interaction.edit_original_message(content=content)
        else:
            await interaction.send(content=content)

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

    @commands.Cog.listener()
    async def on_ready(self):
        # Load games in a global variable for each guild
        gameoflife.init()
        for g in self.bot.guilds:
            gameoflife.games[g.id] = await gameoflifedb.get_by_guild_id(g.id)


def setup(bot):
    bot.add_cog(GameOfLifeCog(bot))
