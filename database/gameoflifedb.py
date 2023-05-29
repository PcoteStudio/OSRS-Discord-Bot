from database import tilenodedb, teamdb
from internal.databasemanager import instance
from internal.gol.gameoflife import GameOfLife


async def get_by_guild_id(guild_id: int):
    doc = await instance.game_of_life.find_one({'guild_id': guild_id, 'is_archived': False})
    if doc is None:
        return None
    return await doc_to_game(doc)


async def insert(game: GameOfLife):
    doc = {
        '_id': game._id,
        'guild_id': game.guild_id,
        'name': game.name,
        'is_archived': game.is_archived
    }
    return await instance.game_of_life.insert_one(doc)


async def archive(game: GameOfLife):
    game.is_archived = True
    result = await instance.game_of_life.update_one({'_id': game._id}, {'$set': {'is_archived': game.is_archived}})
    return result


async def doc_to_game(doc):
    game = GameOfLife(doc['guild_id'], doc['name'], doc['_id'])
    game.is_archived = doc['is_archived']
    game.tiles = await tilenodedb.get_all_by_game_id(game._id)
    game.teams = await teamdb.get_all_by_game_id(game._id)
    return game
