import nextcord
from nextcord.ext import application_checks


def is_gol_admin():
    def predicate(interaction: nextcord.Interaction):
        return True  # Until implemented
    return application_checks.check(predicate)


def is_in_guild():
    def predicate(interaction: nextcord.Interaction):
        return isinstance(interaction.guild, nextcord.Guild)
    return application_checks.check(predicate)


def mention_to_id(mention: str):
    if mention.startswith('<@') and mention.endswith('>'):
        try:
            return int(mention[2:-1])
        except ValueError:
            pass
    return None


async def convert_mentions_string_into_members(guild: nextcord.Guild, mentions: str, separator=' '):
    split = mentions.split()
    members = []
    for s in split:
        id = mention_to_id(s)
        if id is None:
            continue
        m = await guild.fetch_member(id)
        if m is None:
            continue
        members.append(m)
    return members
