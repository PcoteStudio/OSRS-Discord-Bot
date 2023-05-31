from src.internal.gol.team import Team
from bson.objectid import ObjectId
from src.internal.gol import boardgenerator

games = {}


def init():
    global games
    games = {}


def get_game(guild_id: int):
    if guild_id in games:
        return games[guild_id]
    return None


class GameOfLife:
    def __init__(self, guild_id: int, name: str, _id=None):
        self._id = _id or ObjectId()
        self.guild_id = guild_id
        self.name = name
        self.is_archived = False
        self.teams = []
        self.tiles = []

    def roll(self, team):
        pass

    async def generate_board(self):
        self.tiles = boardgenerator.generate_board(self._id)

    def load_tiles(self, tiles_content):
        boardgenerator.load_tiles(self.tiles, tiles_content)

    def add_team(self, team: Team):
        if team not in self.teams:
            self.teams.append(team)

    def remove_team(self, team: Team):
        if team in self.teams:
            self.teams.remove(team)

    def get_teams_as_string(self, separator: str, include_emoji=True):
        result = ""
        for team in self.teams:
            result += f"{team.emoji+' ' if include_emoji else ''}{team.name}{separator}"
        if len(self.members) > 0:
            result = result[:-len(separator)]
        return result
