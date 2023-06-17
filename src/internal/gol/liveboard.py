import calendar
import logging
import os
import math
import copy
from datetime import datetime
import sys
import traceback
from internal.gol.gameoflife import GameOfLife
from PIL import Image, ImageFont, ImageDraw

from os import listdir
from os.path import isfile, join


async def __open_resize_image(path, width, height):
    frame = Image.open(path)
    frame = frame.resize((width, height))
    return frame


async def generate_animation(game: GameOfLife):
    unixtime = calendar.timegm(datetime.utcnow().utctimetuple())
    path_source = f"{os.getcwd()}/out/{game.guild_id}/{game._id}/"
    path_out = f"{os.getcwd()}/out/{game.guild_id}/{game._id}/gif/gif_{unixtime}.gif"
    os.makedirs(os.path.dirname(path_source), exist_ok=True)
    os.makedirs(os.path.dirname(path_out), exist_ok=True)

    images = []
    files = [f for f in listdir(path_source) if isfile(join(path_source, f))]
    max_files = 50
    ratio = 1
    if len(files) > max_files:
        ratio = math.ceil(len(files)/max_files)
    for i, file in enumerate(files):
        try:
            if i % ratio == 0 or i == 0 or i == len(files) - 1:
                images.append(await __open_resize_image(path_source + file, 703, 853))
        except Exception as e:
            logging.error(e)
            traceback.print_exception(*sys.exc_info())

    images[0].save(path_out,
                   save_all=True,
                   optimize=True,
                   append_images=images[1:],
                   duration=300,
                   loop=0)

    return path_out


def draw_game(game: GameOfLife):
    path_board = os.path.join(os.getcwd() + f"/src/boards/{game.file_name}.webp")
    path_font = os.path.join(os.getcwd() + "/src/fonts/SEGUIEMJ.TTF")
    unixtime = calendar.timegm(datetime.utcnow().utctimetuple())
    path_out = f"{os.getcwd()}/out/{game.guild_id}/{game._id}/board_{unixtime if game.is_in_progress() else ''}.webp"
    os.makedirs(os.path.dirname(path_out), exist_ok=True)

    img = Image.open(path_board)
    drawn = ImageDraw.Draw(img)
    mf = ImageFont.truetype(path_font, 100)

    # Find all tiles with teams on them
    populated_tiles = []
    for team in game.teams:
        tile = game.get_current_tile(team)
        pop_tile = next((t for t in populated_tiles if t._id == tile._id), None)
        if (pop_tile == None):
            if (len(tile.pawn_locations) == 0):
                continue
            pop_tile = copy.deepcopy(tile)
            pop_tile.teams = []
            populated_tiles.append(pop_tile)
        pop_tile.teams.append(team)

    # Draw each team emoji on their current tiles
    for pop_tile in populated_tiles:
        for i, team in enumerate(pop_tile.teams):
            res = divmod(i, len(pop_tile.pawn_locations))
            loc_depth = res[0]
            loc_index = res[1]
            loc = pop_tile.pawn_locations[loc_index]
            offsets = pop_tile.pawn_offsets
            drawn.text((loc[0] + loc_depth * offsets[0], loc[1] + loc_depth *
                        offsets[1]), team.emoji[0], fill=tuple(team.color), font=mf)
    img.save(path_out)
    return path_out
