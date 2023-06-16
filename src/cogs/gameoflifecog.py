import asyncio
import traceback
import sys
import logging
import os
import json
import nextcord
from datetime import datetime, timezone
from nextcord import InvalidArgument
from nextcord.ext import tasks, commands, application_checks
from internal import choiceform, constants, utils
from internal.gol import gameoflife, golchecks, golutils, liveboard, golstats
from internal.gol.gameoflife import GameOfLife
from database import teamdb, tilenodedb, gameoflifedb


class GameOfLifeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_updating_boards = False

    @nextcord.slash_command(guild_ids=constants.COMMANDS_GUILD_ID)
    async def gol(self, interaction, test):
        pass

    @gol.subcommand(description="Create a new GoL session on the server.")
    @application_checks.guild_only()
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    async def create(self, interaction: nextcord.Interaction, name: str):
        game_was_archived = False
        game = gameoflife.get_game(interaction.guild.id)
        if game is not None:
            await interaction.send(f'A GoL session already exists for this server. Do you wish to overwrite **{game.name}**?')
            choice, user = await choiceform.slash_choose(self.bot, interaction, [constants.EMOJI_CONFIRM, constants.EMOJI_CANCEL])
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
                logging.info(
                    f"{utils.format_guild_log(interaction.guild)} The existing GoL session {game.name} has been archived by {user.name}.")
                await interaction.edit_original_message(content=f"The existing GoL session **{game.name}** has been archived.")
                game_was_archived = True

        game = GameOfLife(interaction.guild.id, name)
        game.generate_board()
        await gameoflifedb.insert(game)
        await tilenodedb.insert_many(game.tiles)
        gameoflife.games[game.guild_id] = game
        logging.info(
            f"{utils.format_guild_log(interaction.guild)} The GoL session {name} was successfully created for this server by {interaction.user.name}.")
        content = f"The GoL session **{name}** was successfully created for this server."
        if game_was_archived:
            await interaction.edit_original_message(content=content)
        else:
            await interaction.send(content)
        game.is_board_updated = False

    @gol.subcommand(description="Archive the active GoL session of the server.")
    @application_checks.guild_only()
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    @golchecks.game_exists()
    async def archive(self, interaction: nextcord.Interaction):
        game = gameoflife.get_game(interaction.guild.id)
        await interaction.send(f'Do you really wish to archive the GoL session **{game.name}** from this server?')
        choice, user = await choiceform.slash_choose(self.bot, interaction, [constants.EMOJI_CONFIRM, constants.EMOJI_CANCEL])
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
            logging.info(
                f"{utils.format_guild_log(interaction.guild)} The existing GoL session {game.name} has been archived by {user.name}.")
            await interaction.edit_original_message(content=f"The existing GoL session **{game.name}** has been archived.")

    @gol.subcommand(description="Load a board configuration into the active GoL session.")
    @application_checks.guild_only()
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    @golchecks.game_exists()
    async def load(self, interaction: nextcord.Interaction, filename: str):
        game = gameoflife.get_game(interaction.guild.id)
        path = os.path.join(os.getcwd() + f"/src/tiles/{filename}.json")
        if os.path.isfile(path) == False:
            await interaction.send(f"{constants.EMOJI_INCORRECT} The file {filename} doesn't exist.")
            return
        with open(path, 'r', encoding='utf-8') as doc:
            content = json.load(doc)
            game.load_tiles(content)
        await tilenodedb.update_many(game.tiles)
        await teamdb.update_many(game.teams)
        await gameoflifedb.update(game)
        game.is_board_updated = False
        logging.info(
            f"{utils.format_guild_log(interaction.guild)} Tiles loaded successfully for the GoL session {game.name} by {interaction.user.name}.")
        await interaction.send(f"Tiles loaded successfully for the GoL session **{game.name}**.")

    @gol.subcommand(description="Set the start time (UTC) of the active GoL session.")
    @application_checks.guild_only()
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    @golchecks.game_exists()
    async def starttime(self, interaction: nextcord.Interaction, year: int, month: int, day: int, hour: int, minute: int):
        game = gameoflife.get_game(interaction.guild.id)
        game.set_start_time(datetime(year, month, day, hour, minute=minute, tzinfo=timezone.utc).replace(tzinfo=None))
        await gameoflifedb.update(game)
        logging.info(
            f"{utils.format_guild_log(interaction.guild)} Start time set to {game.start_time.strftime(constants.DATE_FORMAT)} for the GoL session {game.name} by {interaction.user.name}.")
        await interaction.send(f"Start time set to UTC {game.start_time.strftime(constants.DATE_FORMAT)} for the GoL session **{game.name}**.")

    @gol.subcommand(description="Set the end time (UTC) of the active GoL session.")
    @application_checks.guild_only()
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    @golchecks.game_exists()
    async def endtime(self, interaction: nextcord.Interaction, year: int, month: int, day: int, hour: int, minute: int):
        game = gameoflife.get_game(interaction.guild.id)
        game.end_time = datetime(year, month, day, hour, minute=minute, tzinfo=timezone.utc).replace(tzinfo=None)
        await gameoflifedb.update(game)
        logging.info(
            f"{utils.format_guild_log(interaction.guild)} End time set to {game.end_time.strftime(constants.DATE_FORMAT)} for the GoL session {game.name} by {interaction.user.name}.")
        await interaction.send(f"End time set to UTC {game.end_time.strftime(constants.DATE_FORMAT)} for the GoL session **{game.name}**.")

    @nextcord.slash_command(guild_ids=constants.COMMANDS_GUILD_ID, description="Roll for your next task.")
    @application_checks.guild_only()
    @golchecks.game_is_ready()
    @golchecks.game_is_in_progress()
    @golchecks.player_is_in_team()
    async def roll(self, interaction: nextcord.Interaction):
        game = gameoflife.get_game(interaction.guild.id)
        team = game.get_team_by_player_id(interaction.user.id)

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
            choice, user = await choiceform.slash_choose(self.bot, interaction, [constants.EMOJI_CONFIRM, constants.EMOJI_CANCEL], team.get_members_id())
            if choice == None:
                await interaction.edit_original_message(content=constants.TEXT_THE_COMMAND_HAS_BEEN_CANCELED_AFTER_NO_INTERACTION_FROM_USER)
                return
            elif choice == 1:
                await interaction.edit_original_message(content=constants.TEXT_THE_COMMAND_HAS_BEEN_CANCELED_BY_TEAM_MEMBER)
                return

            logging.info(
                f"{utils.format_guild_log(interaction.guild)} {interaction.user.name} confirmed the roll completion for {cur_tile.task}.")
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
                choice, user = await choiceform.slash_choose(self.bot, interaction, golutils.get_branch_reactions(destinations), team.get_members_id())
                if choice == None:
                    await interaction.edit_original_message(content=constants.TEXT_THE_COMMAND_HAS_BEEN_CANCELED_AFTER_NO_INTERACTION_FROM_USER)
                    return
                await interaction.edit_original_message(content=content[:-len(constants.TEXT_REACT_TO_THIS_MESSAGE_WITH_CHOICE_DROP_WONT_COUNT)])
                traveled = game.choose_destination(team, destinations[choice])
                content = f"{interaction.user.display_name.title()} has chosen the {'left' if choice == 0 else 'right'} path!\n"
                content += golutils.format_travel(team, destinations[choice], traveled)
                await teamdb.update(team)
                await interaction.followup.send(content)
                await self.post_in_logs_channel(game, golutils.format_roll_log(team, cur_tile, destinations[choice], traveled[-1]))
                game.is_board_updated = False
        finally:
            team.is_rolling = False

    @nextcord.slash_command(guild_ids=constants.COMMANDS_GUILD_ID, description="Rolls back a specific team's last roll.")
    @application_checks.guild_only()
    @application_checks.has_role(constants.ROLE_BOT_ADMIN)
    @golchecks.game_is_ready()
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
            logging.info(
                f"{utils.format_guild_log(interaction.guild)} {interaction.user.name} has rolled back {team.name} to {destination.task}.")
            await interaction.send(content)
            await self.post_in_logs_channel(game, content + "\n" + constants.TEXT_MESSAGE_SEPARATOR)
            game.is_board_updated = False
        finally:
            team.is_rolling = False

    @nextcord.slash_command(guild_ids=constants.COMMANDS_GUILD_ID, description="Displays your current task.")
    @application_checks.guild_only()
    @golchecks.game_is_ready()
    @golchecks.player_is_in_team()
    async def current(self, interaction: nextcord.Interaction):
        game = gameoflife.get_game(interaction.guild.id)
        team = game.get_team_by_player_id(interaction.user.id)

        if game.has_finished(team) == True:
            await interaction.send(f'{constants.EMOJI_INCORRECT} {constants.TEXT_YOUR_TEAM_HAS_ALREADY_COMPLETED_BOARD}')
            return

        await interaction.send(f"Your team's current task is:\n{golutils.format_task_multiline(game.get_current_tile(team))}")

    @nextcord.slash_command(guild_ids=constants.COMMANDS_GUILD_ID, description="Displays statistics about all teams or a specific one.")
    @application_checks.guild_only()
    @golchecks.game_is_ready()
    async def stats(self, interaction: nextcord.Interaction, user: nextcord.User = None):
        game = gameoflife.get_game(interaction.guild.id)
        content = ""
        if user:
            team = game.get_team_by_player_id(user.id)
            if (not team):
                raise InvalidArgument(f"{user.display_name} is not a member of any team.")
            content = golstats.get_formatted_team_stats(game, team)
        else:
            content = golstats.get_formatted_game_stats(game)
        await interaction.send(content)

    @commands.Cog.listener()
    async def on_ready(self):
        # Load games in a global variable for each guild
        gameoflife.init()
        for g in self.bot.guilds:
            gameoflife.games[g.id] = await gameoflifedb.get_by_guild_id(g.id)
        logging.info("GoL sessions loaded")
        self.update_board_channel.start()
        self.update_progress_board.start()

    async def post_in_logs_channel(self, game, content):
        if game and game.channel_logs:
            channel = self.bot.get_channel(game.channel_logs)
            await channel.send(content)

    @tasks.loop(hours=23)
    async def update_progress_board(self):
        await asyncio.sleep(utils.seconds_until(6, 0))
        while self.is_updating_boards:
            await asyncio.sleep(1)
        self.is_updating_boards = True
        logging.info(f"Starting GoL progress board updates")
        try:
            now = datetime.utcnow().replace(tzinfo=None)
            for guild_id, game in gameoflife.games.items():
                if game is None or not game.is_ready() or game.channel_board is None:
                    continue
                if now < game.start_time or now > game.end_time:
                    continue

                channel = self.bot.get_channel(game.channel_board)
                botMsgs = [msg async for msg in channel.history()]
                if len(botMsgs) < 2:
                    continue

                path_out = await liveboard.generate_animation(game)
                content = "Progress board (updated daily)"
                file = nextcord.File(path_out)

                for i, msg in enumerate(reversed(botMsgs)):
                    if (i == 2):
                        await msg.edit(content=content, file=file)
                if len(botMsgs) < 3:
                    await channel.send(content, file=file)
                logging.info(
                    f"{utils.format_guild_log(guild_id)} GoL progress board updated ({golutils.format_game_log(game)})")
        except Exception as error:
            logging.error(error)
            traceback.print_exception(*sys.exc_info())
        finally:
            self.is_updating_boards = False
            logging.info(f"Finished GoL progress board updates")

    @tasks.loop(seconds=2)
    async def update_board_channel(self):
        if self.is_updating_boards:
            return
        self.is_updating_boards = True
        try:
            for guild_id, game in gameoflife.games.items():
                if game is None or not game.is_ready() or game.channel_board is None or game.is_board_updated:
                    continue
                game.is_board_updated = None

                original_board_path = os.path.join(os.getcwd() + "/src/boards/pound.webp")
                updated_board_path = liveboard.draw_game(game)
                channel = self.bot.get_channel(game.channel_board)
                content = ["Reference board", "Updated board"]
                files = [nextcord.File(original_board_path), nextcord.File(updated_board_path)]
                botMsgs = [msg async for msg in channel.history()]

                for i, msg in enumerate(reversed(botMsgs)):
                    if (i < len(content)):
                        await msg.edit(content=content[i], file=files[i])

                i = len(botMsgs)
                for j in range(i, len(content)):
                    await channel.send(content[j], file=files[j])
                if (game.is_board_updated == None):
                    game.is_board_updated = True
                logging.info(
                    f"{utils.format_guild_log(guild_id)} GoL board updated ({golutils.format_game_log(game)})")
        except Exception as error:
            logging.error(error)
            traceback.print_exception(*sys.exc_info())
        finally:
            self.is_updating_boards = False

    @gol.error
    @roll.error
    @rollback.error
    @stats.error
    async def check_failure_error(self, interaction: nextcord.Interaction, error: Exception):
        if not isinstance(error, (nextcord.ApplicationCheckFailure, nextcord.ClientException)):
            raise error


def setup(bot):
    bot.add_cog(GameOfLifeCog(bot))
