import random
import logging
import os
import json
import nextcord
from nextcord.ext import commands
from internal import choiceform, utils, constants
from internal.gol import gameoflife
from internal.gol import golutils
from internal.gol.gameoflife import GameOfLife
from database import teamdb, tilenodedb, gameoflifedb


class GameOfLifeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @utils.is_in_guild()
    @nextcord.slash_command(guild_ids=[1114607456304246784])
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
                await interaction.edit_original_message(content=constants.TEXT_THE_COMMAND_HAS_BEEN_CANCELED_AFTER_NO_INTERACTION_FROM_USER)
                return
            elif choice == 1:
                await interaction.edit_original_message(content=constants.TEXT_THE_COMMAND_HAS_BEEN_CANCELED_BY_TEAM_MEMBER)
                return
            else:
                game.is_archived = True
                await gameoflifedb.update(game)
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
            await interaction.send(f'{constants.EMOJI_INCORRECT} {constants.TEXT_NO_ACTIVE_GOL_SESSION_ON_SERVER}')
            return
        await interaction.send(f'Do you really wish to archive the GoL session **{game.name}** from this server?')
        choice = await choiceform.slash_choose(self.bot, interaction, [constants.EMOJI_CONFIRM, constants.EMOJI_CANCEL])
        if choice == None:
            await interaction.edit_original_message(content=constants.TEXT_THE_COMMAND_HAS_BEEN_CANCELED_AFTER_NO_INTERACTION_FROM_USER)
            return
        elif choice == 1:
            await interaction.edit_original_message(content=constants.TEXT_THE_COMMAND_HAS_BEEN_CANCELED_BY_USER)
            return
        else:
            game.is_archived = True
            await gameoflifedb.update(game)
            gameoflife.games[game.guild_id] = None
            await interaction.edit_original_message(content=f'The existing GoL session **{game.name}** has been archived.')

    @gol.subcommand()
    @utils.is_gol_admin()
    async def load(self, interaction: nextcord.Interaction, filename: str):
        game = gameoflife.get_game(interaction.guild.id)
        if game is None:
            await interaction.send(f'{constants.EMOJI_INCORRECT} {constants.TEXT_NO_ACTIVE_GOL_SESSION_ON_SERVER}')
            return

        path = os.path.join(os.getcwd() + "/src/tiles/", filename)
        if os.path.isfile(path) == False:
            await interaction.send(f":x: The file {filename} doesn't exist.")
            return
        with open(path, 'r', encoding='utf-8') as doc:
            content = json.load(doc)
            game.load_tiles(content)
            await tilenodedb.update_many(game.tiles)
            await teamdb.update_many(game.teams)
            await gameoflifedb.update(game)
            await interaction.send(f"Tiles loaded successfully.")

    @utils.is_in_guild()
    @nextcord.slash_command(guild_ids=[1114607456304246784])
    async def roll(self, interaction: nextcord.Interaction):
        game = gameoflife.get_game(interaction.guild.id)
        if game is None:
            await interaction.send(f'{constants.EMOJI_INCORRECT} {constants.TEXT_NO_ACTIVE_GOL_SESSION_ON_SERVER}')
            return

        team = game.get_team_by_player_id(interaction.user.id)
        if team is None:
            await interaction.send(f'{constants.EMOJI_INCORRECT} {constants.TEXT_YOU_ARE_NOT_MEMBER_OF_ANY_TEAM}')
            return

        if team.is_rolling:
            await interaction.send(f'{constants.EMOJI_INCORRECT} {constants.TEXT_YOUR_TEAM_IS_ALREADY_ROLLING}')
            return
        team.is_rolling = True

        try:
            content = f"{constants.TEXT_HAVE_YOU_COMPLETED_YOUR_PREVIOUS_TASK}\n"
            content += golutils.format_task_multiline(game.get_current_tile(team))
            await interaction.send(content)
            choice = await choiceform.slash_choose(self.bot, interaction, [constants.EMOJI_CONFIRM, constants.EMOJI_CANCEL], team.get_members_id())
            if choice == None:
                await interaction.edit_original_message(content=constants.TEXT_THE_COMMAND_HAS_BEEN_CANCELED_AFTER_NO_INTERACTION_FROM_USER)
                return
            elif choice == 1:
                await interaction.edit_original_message(content=constants.TEXT_THE_COMMAND_HAS_BEEN_CANCELED_BY_TEAM_MEMBER)
                return

            destinations = game.get_possible_destinations(team)
            destinations = destinations[::-1]  # Set left and right properly
            traveled = []
            choice = 0
            content = f"Team {golutils.format_team(team)} rolled a {golutils.format_roll(destinations[0].base_roll, destinations[0].roll)}!\n"
            if len(destinations) == 1:
                traveled = game.choose_destination(team, destinations[0])
                content += golutils.format_travel(team, destinations[choice], traveled)
                await interaction.edit_original_message(content=content)
                await teamdb.update(team)
            if len(destinations) >= 2:
                content += golutils.format_branch(destinations)
                await interaction.edit_original_message(content=content)
                choice = await choiceform.slash_choose(self.bot, interaction, golutils.get_branch_reactions(destinations), team.get_members_id())
                if choice == None:
                    await interaction.edit_original_message(content=constants.TEXT_THE_COMMAND_HAS_BEEN_CANCELED_AFTER_NO_INTERACTION_FROM_USER)
                    return
                await interaction.edit_original_message(content=content[:-len(constants.TEXT_REACT_TO_THIS_MESSAGE_WITH_CHOICE_DROP_WONT_COUNT)])
                traveled = game.choose_destination(team, destinations[choice])
                content = f"{interaction.user.display_name} has chosen the {'left' if choice == 0 else 'right'} path!\n"
                content += golutils.format_travel(team, destinations[choice], traveled)
                await teamdb.update(team)
                await interaction.followup.send(content)
        finally:
            team.is_rolling = False

    @utils.is_in_guild()
    @nextcord.slash_command(guild_ids=[1114607456304246784])
    async def rollback(self, interaction: nextcord.Interaction, user: nextcord.User):
        game = gameoflife.get_game(interaction.guild.id)
        if game is None:
            await interaction.send(f'{constants.EMOJI_INCORRECT} {constants.TEXT_NO_ACTIVE_GOL_SESSION_ON_SERVER}')
            return

        team = game.get_team_by_player_id(user.id)
        if team is None:
            await interaction.send(f'{constants.EMOJI_INCORRECT} {constants.TEXT_THIS_PLAYER_IS_NOT_IN_ANY_TEAM}')
            return

        if team.is_rolling:
            await interaction.send(f'{constants.EMOJI_INCORRECT} {constants.TEXT_THAT_TEAM_IS_CURRENTLY_ROLLING}')
            return
        team.is_rolling = True

        try:
            destination = team.roll_back(game.tiles)
            if destination is None:
                await interaction.send(f'{constants.EMOJI_INCORRECT} {constants.TEXT_THAT_TEAM_CANNOT_BE_ROLLED_BACK_ANY_FURTHER}')
                return
            content = f"Team {golutils.format_team(team)} has been rolled back to this task:\n"
            content += f"{golutils.format_task_multiline(destination)}"
            await teamdb.update(team)
            await interaction.send(content)
        finally:
            team.is_rolling = False

    @commands.Cog.listener()
    async def on_ready(self):
        # Load games in a global variable for each guild
        gameoflife.init()
        for g in self.bot.guilds:
            gameoflife.games[g.id] = await gameoflifedb.get_by_guild_id(g.id)
        logging.info("GoL sessions loaded")


def setup(bot):
    bot.add_cog(GameOfLifeCog(bot))
