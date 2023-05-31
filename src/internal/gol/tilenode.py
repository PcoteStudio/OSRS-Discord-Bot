from bson.objectid import ObjectId
from enum import Enum


class TileType(Enum):
    ORANGE = 0
    GREEN = 1
    RED = 2
    BLUE = 3
    GRAY = 4


class TileNode:
    def __init__(self, game_id: ObjectId, index: int, type: TileType = TileType.ORANGE, task: str = '', _id: ObjectId = None):
        self._id = _id or ObjectId()
        self.game_id = game_id
        self.index = index
        self.task = task
        self.type = type
        self.pawn_location = (0, 0)
        self.pawn_direction = 0
        self.pawn_offset = 10
        self.exits = []
        self.entrances = []

    def partial_parse(self, json):
        self.task = json.get('task', self.task)
        self.type = json.get('type', self.type)

    def get_options(self, node: "TileNode", depth: int):
        if depth <= 0:
            return [node]

        options = []
        for e in node.exits:
            options += self.get_options(e, depth - 1)
        return options

    def add_exit(self, tile: "TileNode"):
        if tile not in self.exits:
            self.exits.append(tile)

    def remove_exit(self, tile: "TileNode"):
        if tile in self.exits:
            self.exits.remove(tile)

    def add_entrance(self, tile: "TileNode"):
        if tile not in self.entrances:
            self.entrances.append(tile)

    def remove_entrance(self, tile: "TileNode"):
        if tile in self.entrances:
            self.entrances.remove(tile)
