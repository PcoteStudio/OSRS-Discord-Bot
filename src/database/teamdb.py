from src.internal.databasemanager import instance
from src.internal.gol.team import Team
from collections.abc import Iterable


async def get_all_by_game_id(game_id: int, limit=1000):
    docs = await instance.team.find({'game_id': game_id}).sort('index').to_list(length=limit)
    if docs is None:
        return []

    teams = []
    for t in docs:
        team = doc_to_team(t)
        teams.append(team)

    return teams


async def insert(team: Team):
    doc = team_to_doc(team)
    return await instance.team.insert_one(doc)


async def insert_many(teams: Iterable[Team]):
    docs = []
    for team in teams:
        doc = team_to_doc(team)
        docs.append(doc)
    return await instance.team.insert_many(docs)


async def delete(team: Team):
    result = await instance.team.delete_one({'_id': team._id})
    return result


def team_to_doc(team: Team):
    return {
        '_id': team._id,
        'game_id': team.game_id,
        'name': team.name,
        'emoji': team.emoji,
        'members': team.members,
    }


def doc_to_team(doc):
    team = Team(doc['game_id'], doc['name'], doc['emoji'], doc['_id'])
    team.members = doc['members']
    return team
