import datetime
import nextcord


def format_guild_log(guild):
    return f"[G#{guild.id if isinstance(guild, nextcord.Guild) else guild}]"


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


def seconds_until(hours, minutes):
    given_time = datetime.time(hours, minutes, tzinfo=datetime.timezone.utc).replace(tzinfo=None)
    now = datetime.datetime.utcnow().replace(tzinfo=None)
    future_exec = datetime.datetime.combine(now, given_time)
    if (future_exec - now).days < 0:
        future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time)
    return (future_exec - now).total_seconds()
