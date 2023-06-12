
from functools import reduce
from internal.gol.gameoflife import GameOfLife
from internal.gol.team import Team
from internal.gol.tilenode import TileNode, TileType


def custom_get_all(game: GameOfLife, team_func, pass_tiles=False):
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
    total = 0
    while tile.type != TileType.GRAY:
        options = TileNode.get_options(tile, len(tiles))
        tile = reduce(lambda a, b: a if a.early > b.early else b, options)
        total += len(tiles) - tile.early
    return total


def get_all_average_total_rolls(game: GameOfLife):
    return custom_get_all(game, get_team_avg_total_roll)


def get_all_tiles_speed(game: GameOfLife):
    return custom_get_all(game, get_team_tiles_speed, True)


def get_all_tiles_before_end(game: GameOfLife):
    return custom_get_all(game, get_team_tiles_before_end, True)
