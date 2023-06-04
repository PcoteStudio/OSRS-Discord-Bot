from src.internal.gol.gameoflife import GameOfLife
from datetime import datetime, date
from bson.objectid import ObjectId
import pytest


class TestGameOfLife:
    guild_id = 123456789
    name = "My Game of Life"
    game_doc = {
        "_id": ObjectId(),
        "is_archived": True,
        "start_time": date(2020, 1, 7),
        "end_time": date(2030, 12, 25)
    }

    def test_full_initialization(self):
        game = GameOfLife(self.guild_id, self.name, self.game_doc)
        assert game.guild_id == self.guild_id
        assert game.name == self.name
        assert game._id == self.game_doc["_id"]
        assert game.is_archived == self.game_doc["is_archived"]
        assert game.start_time == self.game_doc["start_time"]
        assert game.end_time == self.game_doc["end_time"]
