import nextcord
from collections.abc import Iterable


class Team:
    def __init__(self, name, emoji, members: Iterable[nextcord.Member] = []):
        self.name = name
        self.emoji = emoji
        self.members = members

    def is_in_team(self, member: nextcord.Member):
        return member in self.members

    def add_member(self, member: nextcord.Member):
        if member not in self.members:
            self.members.append(member)

    def remove_member(self, member: nextcord.Member):
        if member in self.members:
            self.members.remove(member)

    def get_members_as_string(self, separator: str):
        result = ""
        for member in self.members:
            result += f"<@{member.id}>{separator}"
        if len(self.members) > 0:
            result = result[:-len(separator)]
        return result
