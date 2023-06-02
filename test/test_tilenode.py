import pytest
from bson.objectid import ObjectId
from ..src.internal.gol.tilenode import TileType, TileNode


class TestTileNode:
    game_id = ObjectId()
    tile_a_id = ObjectId()
    tileA = TileNode(game_id, 0, TileType.ORANGE, 'Complete something', tile_a_id)

    def test_full_initialization(self):
        assert self.tileA.game_id == self.game_id
        assert self.tileA._id == self.tile_a_id
        assert self.tileA.index == 0
        assert self.tileA.type == TileType.ORANGE
        assert self.tileA.task == 'Complete something'
