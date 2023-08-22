from bson.objectid import ObjectId
from enum import IntEnum


class TileType(IntEnum):
    ORANGE = 0
    GREEN = 1
    RED = 2
    BLUE = 3
    GRAY = 4


class TileNode:
    task = ""
    type = TileType(0)
    move = 0
    buff = 0
    start = False
    examples = None
    pawn_locations = []
    pawn_offsets = [0, 0]

    def __init__(self, game_id: ObjectId, index: int, doc={}):
        self._id = doc.get("_id", ObjectId())
        self.game_id = game_id
        self.index = index
        self.exits = []
        self.entrances = []
        self.partial_parse(doc)

    def partial_parse(self, json):
        self.task = json.get("task", self.task)
        self.type = TileType(json.get("type", self.type))
        self.move = json.get("move", self.move)
        self.buff = json.get("buff", self.buff)
        self.start = json.get("start", self.start)
        self.examples = json.get("examples", self.examples)
        self.pawn_locations = json.get("pawn_locations", self.pawn_locations)
        self.pawn_offsets = json.get("pawn_offsets", self.pawn_offsets)

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

    @staticmethod
    def get_moved_to(node: "TileNode", depth: int, initial_tile=True):
        if depth == 0 or len(node.exits) == 0 or len(node.entrances) == 0 or (node.type == TileType.RED and initial_tile == False) or node.type == TileType.GRAY:
            return [node]
        if (depth > 0):
            return TileNode.get_moved_to(node.exits[0], depth - 1, False)
        if (depth < 0):
            return TileNode.get_moved_to(node.entrances[0], depth + 1, False)

    @staticmethod
    def get_options(node: "TileNode", depth: int, initial_tile=True):
        if depth <= 0 or len(node.exits) == 0 or (node.type == TileType.RED and initial_tile == False) or node.type == TileType.GRAY:
            node.early = depth
            return [node]

        options = []
        for e in node.exits:
            options += TileNode.get_options(e, depth - 1, False)

        # Remove duplicates
        return list(dict.fromkeys(options))


class Destination(TileNode):

    roll = 0
    base_roll = 0
    early = 0

    def __init__(self, tile: TileNode):
        super().__init__(tile.game_id, tile.index, tile.__dict__)
        for exit in tile.__dict__["exits"]:
            super().add_exit(exit)
        for entrance in tile.__dict__["entrances"]:
            super().add_entrance(entrance)
