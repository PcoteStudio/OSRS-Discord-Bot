from emoji import is_emoji
from nextcord import InvalidArgument
from internal import constants
from internal.sal.snakesandladders import SnakesAndLadders
from internal.sal.tilenode import TileNode
from internal.sal.team import Team


def validate_team_users(members):
    if (len(members) == 0):
        raise InvalidArgument("Enter at least 1 valid user.")


def validate_emoji(emoji: str):
    if (len(emoji) != 1 and not is_emoji(emoji)):
        raise InvalidArgument("Emoji length should be exactly 1 character.")


def validate_team_name(name: str):
    if (len(name) < 1 or len(name) > 50):
        raise InvalidArgument("Name length should be between 1 and 50 characters.")


def format_game_log(game: SnakesAndLadders):
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
        content += f" (*{tile.examples}*)"
    return content


def format_task_multiline(tile: TileNode):
    content = f"Task: **{tile.task}**"
    if tile.examples:
        content += f"\nDetails: *{tile.examples}*"
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
    for t in traveled[1:]:
        content += f"The team keeps going and ends up with the following task:\n"
        content += f"{format_task_multiline(t)}\n"
    return content


def format_roll_log(team, old_tile, destination, new_tile, is_done):
    content = f"Team {format_team(team)} has {'completed' if destination.roll > 0 else 'skipped'} the following task: {format_task(old_tile)}\n"
    if destination.roll > 0:
        content += f"They then rolled {format_roll(destination.base_roll, destination.roll)} and landed on the following task:\n"
    else:
        content += f"They then landed on the following task:\n"
    content += f"{format_task_multiline(new_tile)}\n"
    if is_done:
        content += f"They have already completed this tile, they may roll again.\n"
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
