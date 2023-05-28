
class TileNode:
    def __init__(self, id: int, task: str):
        self.id = id
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
