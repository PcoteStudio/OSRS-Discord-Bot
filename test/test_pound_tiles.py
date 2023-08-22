import json
import pytest
import os
from bson.objectid import ObjectId
from ..src.internal.gol import boardgenerator
from ..src.internal.gol.tilenode import TileType, TileNode


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

    # def test_tiles_raids_qc(self):
    #     nodes = boardgenerator.generate_board(self.game_id)
    #     path = os.path.join(os.getcwd(), "src/tiles/raidsqc.json")
    #     with open(path, 'r', encoding='utf-8') as doc:
    #         content = json.load(doc)
    #         boardgenerator.load_tiles(nodes, content)

    def test_tiles_pound(self):
        nodes = boardgenerator.generate_board(self.game_id)
        path = os.path.join(os.getcwd(), "src/tiles/pound.json")
        with open(path, 'r', encoding='utf-8') as doc:
            content = json.load(doc)
            boardgenerator.load_tiles(nodes, content)

        assert nodes[0].type == TileType.GRAY  # End of board
        assert nodes[76].start == True  # Start of board

        # Branch 1
        options = TileNode.get_options(nodes[76], 2)
        assert len(options) == 2
        assert options[0].index == 74
        assert "2 tiles" in options[0].task
        assert options[1].index == 77
        assert "footwear" in options[1].task

        # Branch 2
        options = TileNode.get_options(nodes[53], 2)  # Fork
        assert len(options) == 1
        assert "mud battlestaff" in options[0].task
        options = TileNode.get_options(nodes[53], 4)  # Paths
        assert len(options) == 2
        assert options[0].index == 46
        assert "zenyte shard" in options[0].task
        assert options[1].index == 50
        assert "dragon battleaxe" in options[1].task
        options = TileNode.get_options(nodes[53], 6)  # Merge
        assert len(options) == 1
        assert options[0].index == 44
        assert "Zulrah" in options[0].task

        # Branch 3
        options = TileNode.get_options(nodes[34], 1)  # Fork
        assert len(options) == 1
        assert "granite longsword" in options[0].task
        options = TileNode.get_options(nodes[34], 3)  # Paths
        assert len(options) == 2
        assert options[0].index == 28
        assert "Venenatis" in options[0].task
        assert options[1].index == 32
        assert "Callisto" in options[1].task
        options = TileNode.get_options(nodes[34], 5)  # Unequal merge
        assert len(options) == 2
        assert options[0].index == 26
        assert "Denying the Healers" in options[0].task
        assert options[1].index == 27
        assert "venator" in options[1].task
