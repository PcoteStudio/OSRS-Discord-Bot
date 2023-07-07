
from functools import reduce
from humanfriendly import format_timespan
from datetime import timedelta
from internal.gol.gameoflife import GameOfLife
from internal.gol.team import Team
from internal.gol.tilenode import TileNode, TileType


def __custom_get_all(game: GameOfLife, team_func, pass_tiles=False):
    stats = []
    for team in game.teams:
        s = team_func(team, game.tiles) if pass_tiles else team_func(team)
        stats.append((team, s))
    return stats


def get_team_avg_total_roll(team: Team):
    total = 0
    count = 0
    for i in range(team.history_index + 1):
        h = team.history[i]
        if h["roll"] > 0:
            total += h["roll"]
            count += 1
    return (None, None) if count == 0 else (round(total / count, 2), count)


def get_team_tiles_speed(team: Team, tiles):
    min_max_times = [None, None]
    min_max_tiles = [None, None]
    previous_tile = None
    previous_h = None
    for i in range(team.history_index + 1):
        h = team.history[i]
        tile = tiles[h["tile_index"]]
        if not previous_tile:
            previous_tile = tile
            previous_h = h
            continue
        if previous_tile.move:
            previous_tile = tile
            previous_h = h
            continue
        time = h["time"] - previous_h["time"]
        time -= timedelta(microseconds=time.microseconds)
        if not min_max_times[0] or time < min_max_times[0]:
            min_max_times[0] = time
            min_max_tiles[0] = previous_tile
        if not min_max_times[1] or time > min_max_times[1]:
            min_max_times[1] = time
            min_max_tiles[1] = previous_tile
        previous_tile = tile
        previous_h = h
    return ((min_max_times[0], min_max_tiles[0]), (min_max_times[1], min_max_tiles[1]))


def get_team_tiles_before_end(team: Team, tiles):
    tile = team.get_current_tile(tiles)
    if not tile:
        return None
    total = 0
    while tile.type != TileType.GRAY:
        options = TileNode.get_options(tile, len(tiles))
        tile = reduce(lambda a, b: a if a.early > b.early else b, options)
        total += len(tiles) - tile.early
    return total


def get_all_average_total_rolls(game: GameOfLife):
    return __custom_get_all(game, get_team_avg_total_roll)


def get_all_tiles_speed(game: GameOfLife):
    return __custom_get_all(game, get_team_tiles_speed, True)


def get_all_tiles_before_end(game: GameOfLife):
    return __custom_get_all(game, get_team_tiles_before_end, True)


def get_formatted_team_stats(game: GameOfLife, team: Team):
    avg_total_roll = get_team_avg_total_roll(team)
    tiles_speed = get_team_tiles_speed(team, game.tiles)
    tiles_before_end = get_team_tiles_before_end(team, game.tiles)
    content = f"Team **{team.name}** {team.emoji} statistics\n```"
    content += f"\nAverage roll: {'N/A' if avg_total_roll[0] is None else avg_total_roll[0]}"
    content += f"\nTotal grinds completed: {0 if avg_total_roll[1] is None else avg_total_roll[1]} grinds"
    content += f"\nNumber of tiles away from board completion: {tiles_before_end} tiles"
    if tiles_speed[1][1]:
        content += f"\nLongest grinds: [{format_timespan(tiles_speed[1][0])}] {tiles_speed[1][1].task}"
    else:
        content += f"\nLongest grinds: N/A"
    if tiles_speed[0][1]:
        content += f"\nFastest grinds: [{format_timespan(tiles_speed[0][0])}] {tiles_speed[0][1].task}"
    else:
        content += f"\nFastest grinds: N/A"
    content += "\n```\n"
    return content


def get_formatted_game_stats(game: GameOfLife):
    all_avg_total_rolls = get_all_average_total_rolls(game)
    content = [format_all_average_rolls(all_avg_total_rolls) + format_all_total_rolls(all_avg_total_rolls),
               format_all_tiles_before_end(get_all_tiles_before_end(game)) + format_all_tiles_speed(get_all_tiles_speed(game))]
    return content


def format_all_total_rolls(all_average_total_rolls):
    content = "**Total grinds completed**```"
    for team, rolls in all_average_total_rolls:
        if (rolls[1] is None):
            content += f"\n- Team {team.name} {team.emoji}: 0"
        else:
            content += f"\n- Team {team.name} {team.emoji}: {rolls[1]} grinds"
    content += "\n```\n"
    return content


def format_all_average_rolls(all_average_total_rolls):
    content = "**Average roll**```"
    for team, rolls in all_average_total_rolls:
        if (rolls[0] is None):
            content += f"\n- Team {team.name} {team.emoji}: N/A"
        else:
            content += f"\n- Team {team.name} {team.emoji}: {rolls[0]}"
    content += "\n```\n"
    return content


def format_all_tiles_before_end(all_tiles_before_end):
    content = "**Number of tiles away from board completion**```"
    for team, tiles in all_tiles_before_end:
        if (tiles is None):
            content += f"\n- Team {team.name} {team.emoji}: N/A"
        else:
            content += f"\n- Team {team.name} {team.emoji}: {tiles} tiles"
    content += "\n```\n"
    return content


def format_all_tiles_speed(all_tiles_speed):
    content_slow = "**Longest grinds**```"
    content_fast = "**Fastest grinds**```"
    for team, speeds in all_tiles_speed:
        slowest = speeds[1]
        fastest = speeds[0]
        if (slowest[1] is not None):
            content_slow += f"\n- Team {team.name} {team.emoji}: [{format_timespan(slowest[0])}] {slowest[1].task}"
        else:
            content_slow += f"\n- Team {team.name} {team.emoji}: N/A"
        if (fastest[1] is not None):
            content_fast += f"\n- Team {team.name} {team.emoji}: [{format_timespan(fastest[0])}] {fastest[1].task}"
        else:
            content_fast += f"\n- Team {team.name} {team.emoji}: N/A"
    content_slow += "\n```\n"
    content_fast += "\n```\n"
    return content_slow + content_fast
