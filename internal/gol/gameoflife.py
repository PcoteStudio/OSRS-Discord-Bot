from internal.gol import Team


class GameOfLife:
    def __init__(self, guild_id: int, name: str):
        self.guild_id = guild_id
        self.name = name
        self.teams = []

    def add_team(self, team: Team):
        if team not in self.teams:
            self.team.append(team)

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
