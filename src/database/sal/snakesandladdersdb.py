import logging
from database.sal import teamdb, tilenodedb
from internal.databasemanager import instance
from internal.sal.snakesandladders import SnakesAndLadders


async def get_by_guild_id(guild_id: int):
    doc = await instance.snakes_and_ladders.find_one({'guild_id': guild_id, 'is_archived': False})
    if doc is None:
        return None
    return await doc_to_game(doc)


async def insert(game: SnakesAndLadders):
    result = await instance.snakes_and_ladders.insert_one(game_to_doc(game))
    logging.info(f"SaL session inserted (_id:{game._id}, name:{game.name})")
    return result


async def update(game: SnakesAndLadders):
    result = await instance.snakes_and_ladders.update_one({'_id': game._id}, {'$set': game_to_doc(game)})
    logging.info(f"SaL session updated (_id:{game._id}, name:{game.name})")
    return result


async def doc_to_game(doc):
    game = SnakesAndLadders(doc['guild_id'], doc['name'], doc)
    game.tiles = await tilenodedb.get_all_by_game_id(game._id)
    game.teams = await teamdb.get_all_by_game_id(game._id)
    return game


def game_to_doc(game: SnakesAndLadders):
    doc = {
        '_id': game._id,
        'guild_id': game.guild_id,
        'name': game.name,
        'is_archived': game.is_archived,
        'start_time': game.start_time,
        'end_time': game.end_time,
        'start_index': game.start_index,
        'channel_logs': game.channel_logs,
        'channel_board': game.channel_board,
        'file_name': game.file_name,
    }
    return doc
