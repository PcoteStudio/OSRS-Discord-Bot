from bson.objectid import ObjectId
from datetime import datetime
from internal.gol import boardgenerator
from internal.gol.team import Team

games = {}


def init():
    global games
    games = {}


def get_game(guild_id: int):
    if guild_id in games:
        return games[guild_id]
    return None


class GameOfLife:
    def __init__(self, guild_id: int, name: str, doc={}):
        self.guild_id = guild_id
        self.name = name
        self._id = doc.get('_id', ObjectId())
        self.is_archived = doc.get('is_archived', False)
        self.start_time = doc.get('start_time', datetime.min)
        self.end_time = doc.get('end_time', datetime.max)
        self.start_index = doc.get('start_index', None)
        self.channel_logs = doc.get('channel_logs', None)
        self.channel_board = doc.get('channel_board', None)
        self.teams = []
        self.tiles = []

        self.is_board_updated = False

    def has_finished(self, team: Team):
        return team.has_finished(self.tiles)

    def set_start_index(self, tile_index):
        if tile_index is None:
            return
        self.start_index = tile_index
        for team in self.teams:
            team.set_start_tile(self.tiles[tile_index])

    def set_event_time(self, start: datetime, end: datetime):
        self.start_time = start
        self.end_time = end

    def get_current_tile(self, team: Team):
        return team.get_current_tile(self.tiles)

    def get_possible_destinations(self, team: Team):
        return team.get_possible_destinations(self.tiles)

    def choose_destination(self, team, destination):
        return team.choose_destination(destination)

    def generate_board(self):
        self.tiles = boardgenerator.generate_board(self._id)

    def load_tiles(self, tiles_content):
        self.set_start_index(boardgenerator.load_tiles(self.tiles, tiles_content))

    def add_team(self, team: Team):
        if team in self.teams:
            return
        self.teams.append(team)
        if self.start_index is not None:
            team.set_start_tile(self.tiles[self.start_index])

    def remove_team(self, team: Team):
        if team in self.teams:
            self.teams.remove(team)

    def get_team_by_player_id(self, player_id: int):
        for team in self.teams:
            if team.is_in_team(player_id):
                return team
        return None

    def get_teams_as_string(self, separator: str, include_emoji=True):
        result = ""
        for team in self.teams:
            result += f"{team.emoji+' ' if include_emoji else ''}{team.name}{separator}"
        if len(self.members) > 0:
            result = result[:-len(separator)]
        return result
