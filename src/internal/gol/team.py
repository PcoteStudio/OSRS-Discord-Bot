import nextcord
from collections.abc import Iterable
from bson.objectid import ObjectId


class Team:
    def __init__(self, game_id: ObjectId, name, emoji: str, _id: ObjectId = None):
        self._id = _id or ObjectId()
        self.game_id = game_id
        self.name = name
        self.emoji = emoji
        self.members = []

    def is_in_team(self, member):
        return any(m['id'] == member.id for m in self.members)

    def add_members(self, members: Iterable):
        for m in members:
            self.add_member(m)

    def add_member(self, member):
        if member not in self.members:
            self.members.append({'id': member.id, 'name': member.name})

    def remove_member(self, member):
        self.members = filter(lambda m: m.id != member['id'], self.members)

    def get_members_as_string(self, separator: str):
        result = ""
        for member in self.members:
            result += f"<@{member['id']}>{separator}"
        if len(self.members) > 0:
            result = result[:-len(separator)]
        return result
