from nextcord import errors
from internal import constants
from internal.gol.gameoflife import GameOfLife
from internal.gol.tilenode import TileNode
from internal.gol.team import Team


def validate_emoji(emoji: str):
    if (len(emoji) != 1):
        raise errors.InvalidArgument("Emoji length should be exactly 1 character.")


def validate_team_name(name: str):
    if (len(name) < 1 or len(name) > 50):
        raise errors.InvalidArgument("Name length should be between 1 and 50 characters.")


def format_game_log(game: GameOfLife):
    return f"game_name:{game.name}, game_id:{game._id}"


def format_roll(base_roll: int, roll: int):
    if base_roll == roll:
        return f"**{roll}**"
    return f"**{roll}** ({base_roll}+{roll-base_roll})"


def format_roll_sentence(team: Team, base_roll: int, roll: int):
    return f"Team {format_team(team)} rolled a {format_roll(base_roll, roll)}!\n"


def format_team(team: Team, include_emoji=True):
    result = f"**{team.name}**"
    if include_emoji:
        result += f" {team.emoji}"
    return result


def format_task(tile: TileNode):
    content = f"**{tile.task}**"
    if tile.examples:
        content += f" (ex: *{tile.examples}*)"
    return content


def format_task_multiline(tile: TileNode):
    content = f"Task: **{tile.task}**"
    if tile.examples:
        content += f"\nExamples: *{tile.examples}*"
    return content


def format_branch(destinations):
    content = "Your path is branching. You will have to choose which branch to take to continue...\n"
    content += f"{constants.EMOJI_LEFT_ARROW} Choose left to {format_task(destinations[0])}.\n"
    if len(destinations) == 3:
        content += f"{constants.EMOJI_UP_ARROW} Choose middle to {format_task(destinations[1])}.\n"
    if len(destinations) == 4:
        content += f"{constants.EMOJI_UPPER_LEFT_ARROW} Choose middle-left to {format_task(destinations[1])}.\n"
        content += f"{constants.EMOJI_UPPER_RIGHT_ARROW} Choose middle-right to {format_task(destinations[2])}.\n"
    content += f"{constants.EMOJI_RIGHT_ARROW} Choose right to {format_task(destinations[-1])}.\n"
    content += constants.TEXT_REACT_TO_THIS_MESSAGE_WITH_CHOICE_DROP_WONT_COUNT
    return content


def format_travel(team, destination, traveled):
    content = f"Team {format_team(team)} advances {destination.roll - destination.early} tiles and lands on the following task:\n"
    content += f"{format_task_multiline(traveled[0])}\n"
    content += format_buff(traveled[0])
    for t in traveled[1:]:
        content += f"The team keeps going and ends up with the following task:\n"
        content += f"{format_task_multiline(t)}\n"
        content += format_buff(t)
    return content


def format_buff(destination):
    if destination.buff == 0:
        return ""
    return f"The team has stopped on a blue tile, **their minimum roll is buffed by 1**!\n"


def format_roll_log(team, old_tile, destination, new_tile):
    content = f"Team {format_team(team)} has completed the following task: {format_task(old_tile)}\n"
    content += f"They then rolled {format_roll(destination.base_roll, destination.roll)} and landed on the following task:\n"
    content += f"{format_task_multiline(new_tile)}\n"
    content += format_buff(new_tile)
    content += constants.TEXT_MESSAGE_SEPARATOR
    return content


def get_branch_reactions(destinations):
    if len(destinations) <= 1:
        return None
    if len(destinations) == 2:
        return [constants.EMOJI_LEFT_ARROW, constants.EMOJI_RIGHT_ARROW]
    if len(destinations) == 3:
        return [constants.EMOJI_LEFT_ARROW, constants.EMOJI_UP_ARROW, constants.EMOJI_RIGHT_ARROW]
    if len(destinations) == 3:
        return [constants.EMOJI_LEFT_ARROW, constants.EMOJI_UPPER_LEFT_ARROW,
                constants.EMOJI_UPPER_RIGHT_ARROW, constants.EMOJI_RIGHT_ARROW]
    raise NotImplementedError(f"Branches can't handle {len(destinations)} paths yet.")
