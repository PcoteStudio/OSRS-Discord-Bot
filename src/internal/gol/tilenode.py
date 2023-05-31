from bson.objectid import ObjectId


class TileNode:
    def __init__(self, game_id: ObjectId, index: int, task: str = '', _id: ObjectId = None):
        self._id = _id or ObjectId()
        self.game_id = game_id
        self.index = index
        self.task = task
        self.pawn_location = (0, 0)
        self.pawn_direction = 0
        self.pawn_offset = 10
        self.exits = []
        self.entrances = []

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
