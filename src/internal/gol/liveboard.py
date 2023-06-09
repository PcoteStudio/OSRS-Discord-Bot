import os
import copy
from internal.gol.gameoflife import GameOfLife
from PIL import Image, ImageFont, ImageDraw


def draw_game(game: GameOfLife):
    path_board = os.path.join(os.getcwd() + "/src/boards/pound.webp")
    path_font = os.path.join(os.getcwd() + "/src/fonts/SEGUIEMJ.ttf")
    path_out = os.path.join(os.getcwd() + "/out/boards/pound_generated.webp")

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
                        offsets[1]), team.emoji, fill=tuple(team.color), font=mf)
    img.save(path_out)
    return path_out
