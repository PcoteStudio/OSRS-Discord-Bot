import json
import pytest
import os
from bson.objectid import ObjectId
from ..src.internal.sal import boardgenerator
from ..src.internal.sal.tilenode import TileType, TileNode


class TestPoundTiles:
    game_id = ObjectId()
    tile_index = 3
    tile_doc = {
        "_id": ObjectId(),
        "type": TileType.ORANGE,
        "task": "Obtain something"
    }

    def test_full_initialization(self):
        tile = TileNode(self.game_id, self.tile_index, self.tile_doc)
        assert tile.game_id == self.game_id
        assert tile._id == self.tile_doc["_id"]
        assert tile.index == self.tile_index
        assert tile.type == self.tile_doc["type"]
        assert tile.task == self.tile_doc["task"]

    def test_tiles_raids_qc(self):
        nodes = boardgenerator.generate_board(self.game_id)
        path = os.path.join(os.getcwd(), "src/tiles/raidsqc.json")
        with open(path, 'r', encoding='utf-8') as doc:
            content = json.load(doc)
            boardgenerator.load_tiles(nodes, content)

        assert nodes[0].type == TileType.GRAY  # End of board
        assert nodes[1].type == TileType.RED  # Last tile is stop tile
        assert nodes[100].start == True  # Start of board

        options = TileNode.get_options(nodes[100], 2)
        assert len(options) == 1
        assert options[0].index == 98
        assert "skull sceptre" in options[0].task
