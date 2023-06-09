import logging
from internal.databasemanager import instance
from internal.gol.team import Team
from pymongo import UpdateOne
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
    result = await instance.team.insert_one(doc)
    logging.info(f"Team inserted (_id:{team._id}, name:{team.name})")
    return result


async def insert_many(teams: Iterable[Team]):
    docs = []
    for team in teams:
        doc = team_to_doc(team)
        docs.append(doc)

    result = await instance.team.insert_many(docs)
    logging.info(f"Multiple teams inserted (len:{len(teams)})")
    return result


async def update(team: Team):
    result = await instance.team.update_one({'_id': team._id}, {'$set': team_to_doc(team)})
    logging.info(f"Team updated (_id:{team._id}, name:{team.name})")
    return result


async def update_many(teams: Iterable[Team]):
    requests = []
    for team in teams:
        r = UpdateOne({"_id": team._id}, {'$set': team_to_doc(team)})
        requests.append(r)
    if len(requests) > 0:
        result = await instance.team.bulk_write(requests, ordered=False)
        logging.info(f"Multiple teams updated (len:{len(teams)})")
        return result


async def delete(team: Team):
    result = await instance.team.delete_one({'_id': team._id})
    logging.info(f"Team deleted (_id:{team._id}, name:{team.name})")
    return result


def team_to_doc(team: Team):
    return {
        '_id': team._id,
        'game_id': team.game_id,
        'name': team.name,
        'emoji': team.emoji,
        'seed': team.seed,
        'buffs': team.buffs,
        'color': team.color,
        'history_index': team.history_index,
        'history': team.history,
        'members': team.members,
    }


def doc_to_team(doc):
    team = Team(doc['game_id'], doc['name'], doc['emoji'], doc)
    return team
