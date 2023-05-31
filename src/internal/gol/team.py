import random
from collections.abc import Iterable
from bson.objectid import ObjectId


class Team:
    def __init__(self, game_id: ObjectId, name, emoji: str, seed: int, _id: ObjectId = None):
        self._id = _id or ObjectId()
        self.game_id = game_id
        self.name = name
        self.emoji = emoji
        self.seed = random.randint(1000, 100000000000)
        self.history_index = None
        self.history = []
        self.members = []

    def rollback(self):
        if self.history_index is None or self.history_index == 0:
            return
        self.history_index -= 1
        self.seed == self.history[self.history_index]['seed']

    def add_to_history(self, seed, roll, tile_index):
        self.history_index += 1
        h = {'seed': seed, 'roll': roll, 'tile_index': tile_index}
        if self.history_index is None or self.history_index == len(self.history):
            self.history.append(h)
        else:
            self.history[self.history_index] = h

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
