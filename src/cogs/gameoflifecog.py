import random
import os
import json
import nextcord
from nextcord.ext import commands
from src.internal import choiceform, utils, constants
from src.internal.gol import gameoflife
from src.internal.gol.gameoflife import GameOfLife
from src.database import tilenodedb, gameoflifedb


class GameOfLifeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @utils.is_in_guild()
    @nextcord.slash_command(guild_ids=[933103168374583417])
    async def gol(self, interaction):
        pass

    @gol.subcommand()
    @utils.is_gol_admin()
    async def create(self, interaction: nextcord.Interaction, name: str):
        game_was_archived = False
        game = gameoflife.get_game(interaction.guild.id)
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
            await interaction.edit_original_message(content)
        else:
            await interaction.send(content)

    @gol.subcommand()
    @utils.is_gol_admin()
    async def archive(self, interaction: nextcord.Interaction):
        game = gameoflife.get_game(interaction.guild.id)
        if game is None:
            await interaction.send(f':x: There is no active GoL session on this server to archive.')
            return
        await interaction.send(f'Do you really wish to archive the GoL session **{game.name}** from this server?')
        choice = await choiceform.slash_choose(self.bot, interaction, [constants.EMOJI_CONFIRM, constants.EMOJI_CANCEL])
        if choice == None:
            await interaction.edit_original_message(content='The GoL session archiving has been canceled after no reaction from the user.')
            return
        elif choice == 1:
            await interaction.edit_original_message(content='The GoL session archiving has been canceled by the user.')
            return
        else:
            await gameoflifedb.archive(game)
            gameoflife.games[game.guild_id] = None
            await interaction.edit_original_message(content=f'The existing GoL session **{game.name}** has been archived.')

    @gol.subcommand()
    @utils.is_gol_admin()
    async def load(self, interaction: nextcord.Interaction, filename: str):
        game = gameoflife.get_game(interaction.guild.id)
        path = os.path.join(os.getcwd() + "\\tiles\\", filename)
        if os.path.isfile(path) == False:
            await interaction.send(f":x: The file {filename} doesn't exist.")
            return
        with open(path, 'r', encoding='utf-8') as doc:
            content = json.load(doc)
            game.load_tiles(content)
            await interaction.send(f"Tiles loaded successfully.")
            

    @commands.command(name="roll")
    @commands.bot_has_permissions(add_reactions=True)
    async def roll(self, ctx):
        # TODO Ask "Did you complete the following task and posted the proof of completion ?"

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
