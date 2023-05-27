import nextcord


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
