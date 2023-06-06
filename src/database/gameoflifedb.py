import logging
from database import tilenodedb, teamdb
from internal.databasemanager import instance
from internal.gol.gameoflife import GameOfLife


async def get_by_guild_id(guild_id: int):
    doc = await instance.game_of_life.find_one({'guild_id': guild_id, 'is_archived': False})
    if doc is None:
        return None
    return await doc_to_game(doc)


async def insert(game: GameOfLife):
    result = await instance.game_of_life.insert_one(game_to_doc(game))
    logging.info(f"GoL session inserted (_id:{game._id}, name:{game.name})")
    return result


async def update(game: GameOfLife):
    result = await instance.game_of_life.update_one({'_id': game._id}, {'$set': game_to_doc(game)})
    logging.info(f"GoL session updated (_id:{game._id}, name:{game.name})")
    return result


async def doc_to_game(doc):
    game = GameOfLife(doc['guild_id'], doc['name'], doc)
    game.tiles = await tilenodedb.get_all_by_game_id(game._id)
    game.teams = await teamdb.get_all_by_game_id(game._id)
    return game


def game_to_doc(game: GameOfLife):
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
    }
    return doc
