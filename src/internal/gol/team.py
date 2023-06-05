import random
from collections.abc import Iterable
from bson.objectid import ObjectId
from internal import constants
from internal.gol.tilenode import TileNode, TileType


class Team:
    def __init__(self, game_id: ObjectId, name, emoji: str, doc={}):
        self._id = doc.get("_id", ObjectId())
        self.game_id = game_id
        self.name = name
        self.emoji = emoji
        self.seed = doc.get("seed", random.randint(1000, 100000000000))
        self.history_index = doc.get("history_index", -1)
        self.buffs = doc.get("buffs", 0)
        self.history = doc.get("history", [])
        self.members = doc.get("members", [])

        self.is_rolling = False

    def has_finished(self, tiles):
        tile = self.get_current_tile(tiles)
        return tile != None and tile.type == TileType.GRAY

    def has_start_tile(self):
        return len(self.history) > 0

    def set_start_tile(self, tile):
        if self.has_start_tile():
            return
        tile.base_roll = 0
        tile.roll = 0
        tile.early = 0
        self.choose_destination(tile)

    def get_current_tile(self, tiles):
        cur_history = self.get_current_history()
        cur_tile = tiles[cur_history['tile_index']]
        return cur_tile

    def get_possible_destinations(self, tiles):
        if self.can_choose_next_destination() == False:
            tile_history = self.history[self.history_index + 1]
            tile = tiles[tile_history['tile_index']]
            tile.roll = tile_history['roll']
            tile.base_roll = tile_history['base_roll']
            tile.early = tile_history['early']
            return [tile]

        cur_history = self.get_current_history()
        cur_tile = tiles[cur_history['tile_index']]
        random.seed(self.seed + 1)
        base_roll = random.randint(constants.MIN_ROLL, constants.MAX_ROLL)
        roll = min(constants.MAX_ROLL, max(base_roll, constants.MIN_ROLL + self.buffs))
        destinations = TileNode.get_options(cur_tile, roll)
        for d in destinations:
            d.roll = roll
            d.base_roll = base_roll
        return destinations

    def choose_destination(self, destination):
        h = {"base_roll": destination.base_roll, "roll": destination.roll,
             "tile_index": destination.index, "early": destination.early}
        # New roll
        if self.history_index == len(self.history) - 1:
            self.history.append(h)
        # Can't change existing roll
        elif destination.index != self.history[self.history_index + 1]["tile_index"]:
            return None
        # New roll
        self.history_index += 1
        self.seed += 1
        self.buffs += destination.buff
        if (destination.move):
            move_destinations = TileNode.get_moved_to(destination, destination.move)
            move_destinations[0].base_roll = 0
            move_destinations[0].roll = 0
            move_destinations[0].early = 0
            new_destinations = self.choose_destination(move_destinations[0])
            return [destination] + new_destinations
        return [destination]

    def roll_back(self, tiles):
        if self.history_index <= 0:
            return None
        cur_history = self.get_current_history()
        self.history_index -= 1
        self.seed -= 1
        # If the game moved the player automatically, get further back
        if (cur_history["roll"] == 0):
            return self.roll_back(tiles)
        return self.get_current_tile(tiles)

    def can_choose_next_destination(self):
        return self.history_index >= len(self.history) - 1

    def roll_forward(self):
        pass

    def get_current_history(self):
        if (self.history_index < 0):
            return None
        return self.history[self.history_index]

    def is_in_team(self, player_id):
        return any(m['id'] == player_id for m in self.members)

    def add_members(self, members: Iterable):
        for m in members:
            self.add_member(m)

    def add_member(self, member):
        if member not in self.members:
            self.members.append({'id': member.id, 'name': member.display_name})

    def remove_member(self, member):
        self.members = filter(lambda m: m.id != member['id'], self.members)

    def get_members_id(self):
        return map(lambda m: m["id"], self.members)

    def get_members_as_string(self, ping: bool, separator: str):
        result = ""
        for member in self.members:
            result += f"<@{member['id']}>{separator}" if ping else f"{member['name']}{separator}"
        if len(self.members) > 0:
            result = result[:-len(separator)]
        return result
