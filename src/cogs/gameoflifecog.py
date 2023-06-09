import random
import logging
import os
import json
import nextcord
from nextcord.ext import tasks, commands
from internal import choiceform, utils, constants
from internal.gol import gameoflife, golutils, liveboard
from internal.gol.gameoflife import GameOfLife
from database import teamdb, tilenodedb, gameoflifedb


class GameOfLifeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_updating_boards = False

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
        game.generate_board()
        await gameoflifedb.insert(game)
        await tilenodedb.insert_many(game.tiles)
        gameoflife.games[game.guild_id] = game
        content = f"A GoL session **{name}** was successfully created for this server."
        if game_was_archived:
            await interaction.edit_original_message(content=content)
        else:
            await interaction.send(content)
        game.is_board_updated = False

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
            game.is_board_updated = False

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

        if game.has_finished(team) == True:
            await interaction.send(f'{constants.EMOJI_INCORRECT} {constants.TEXT_YOUR_TEAM_HAS_ALREADY_COMPLETED_BOARD}')
            return

        if team.is_rolling:
            await interaction.send(f'{constants.EMOJI_INCORRECT} {constants.TEXT_YOUR_TEAM_IS_ALREADY_ROLLING}')
            return
        team.is_rolling = True

        try:
            cur_tile = game.get_current_tile(team)
            content = f"{constants.TEXT_HAVE_YOU_COMPLETED_YOUR_PREVIOUS_TASK}\n"
            content += golutils.format_task_multiline(cur_tile)
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
            content = golutils.format_roll_sentence(
                team, destinations[0].base_roll, destinations[0].roll)
            if len(destinations) == 1:
                traveled = game.choose_destination(team, destinations[choice])
                content += golutils.format_travel(team, destinations[choice], traveled)
                await interaction.edit_original_message(content=content)
                await teamdb.update(team)
                await self.post_in_logs_channel(game, golutils.format_roll_log(team, cur_tile, destinations[choice], traveled[-1]))
                game.is_board_updated = False
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
                await self.post_in_logs_channel(game, golutils.format_roll_log(team, cur_tile, destinations[choice], traveled[-1]))
                game.is_board_updated = False
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
            await self.post_in_logs_channel(game, content + "\n" + constants.TEXT_MESSAGE_SEPARATOR)
            game.is_board_updated = False
        finally:
            team.is_rolling = False

    @utils.is_in_guild()
    @nextcord.slash_command(guild_ids=[1114607456304246784])
    async def current(self, interaction: nextcord.Interaction):
        game = gameoflife.get_game(interaction.guild.id)
        if game is None:
            await interaction.send(f'{constants.EMOJI_INCORRECT} {constants.TEXT_NO_ACTIVE_GOL_SESSION_ON_SERVER}')
            return

        team = game.get_team_by_player_id(interaction.user.id)
        if team is None:
            await interaction.send(f'{constants.EMOJI_INCORRECT} {constants.TEXT_YOU_ARE_NOT_MEMBER_OF_ANY_TEAM}')
            return

        if game.has_finished(team) == True:
            await interaction.send(f'{constants.EMOJI_INCORRECT} {constants.TEXT_YOUR_TEAM_HAS_ALREADY_COMPLETED_BOARD}')
            return

        await interaction.send(f"Your team's current task is:\n{golutils.format_task_multiline(game.get_current_tile(team))}")

    @commands.Cog.listener()
    async def on_ready(self):
        # Load games in a global variable for each guild
        gameoflife.init()
        for g in self.bot.guilds:
            gameoflife.games[g.id] = await gameoflifedb.get_by_guild_id(g.id)
        logging.info("GoL sessions loaded")
        self.update_board_channel.start()

    async def post_in_logs_channel(self, game, content):
        if game and game.channel_logs:
            channel = self.bot.get_channel(game.channel_logs)
            await channel.send(content)

    @tasks.loop(seconds=2)
    async def update_board_channel(self):
        if self.is_updating_boards:
            return
        self.is_updating_boards = True
        try:
            for guild_id, game in gameoflife.games.items():
                if game is None or game.channel_board is None or game.is_board_updated:
                    continue
                game.is_board_updated = None
                original_board_path = os.path.join(os.getcwd() + "/src/boards/pound.webp")
                updated_board_path = liveboard.draw_game(game)
                channel = self.bot.get_channel(game.channel_board)

                botMsgs = [msg async for msg in channel.history()]

                content = ["Reference board", "Updated board"]
                files = [nextcord.File(original_board_path), nextcord.File(updated_board_path)]

                for i, msg in enumerate(reversed(botMsgs)):
                    if (i >= len(content)):
                        await msg.delete()
                    else:
                        await msg.edit(content=content[i], file=files[i])

                i = len(botMsgs)
                for j in range(i, len(content)):
                    await channel.send(content[j], file=files[j])
                if (game.is_board_updated == None):
                    game.is_board_updated = True
                logging.info(f"GoL board updated (game_id:{game._id}, game_name:{game.name})")
        finally:
            self.is_updating_boards = False
            self.update_board_channel.restart()


def setup(bot):
    bot.add_cog(GameOfLifeCog(bot))
