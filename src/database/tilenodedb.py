from internal.databasemanager import instance
from internal.gol.tilenode import TileNode
from collections.abc import Iterable
from pymongo import UpdateOne


async def get_all_by_game_id(game_id: int, limit=1000):
    docs = await instance.tile_node.find({'game_id': game_id}).sort('index').to_list(length=limit)
    if docs is None:
        return []

    tiles = []
    for t in docs:
        tile = doc_to_tile(t)
        tiles.append(tile)
    for t in docs:
        if t['exits'] is None:
            continue
        for exit_id in t['exits']:
            exit = next(x for x in tiles if x._id == exit_id)
            tiles[t['index']].exits.append(exit)
            tiles[exit.index].entrances.append(tiles[t['index']])
    return tiles


async def insert_many(tiles: Iterable[TileNode]):
    docs = []
    for tile in tiles:
        doc = tile_to_doc(tile)
        docs.append(doc)
    return await instance.tile_node.insert_many(docs)


async def update_many(tiles: Iterable[TileNode]):
    requests = []
    for tile in tiles:
        r = UpdateOne({"_id": tile._id}, {'$set': tile_to_doc(tile)})
        requests.append(r)
    if len(requests) > 0:
        return await instance.tile_node.bulk_write(requests, ordered=False)


def doc_to_tile(doc):
    node = TileNode(doc.get('game_id'), doc.get('index'), doc)
    return node


def tile_to_doc(tile: TileNode):
    doc = {
        '_id': tile._id,
        'game_id': tile.game_id,
        'index': tile.index,
        'type': tile.type,
        'task': tile.task,
        'examples': tile.examples,
        'type': tile.type,
        'move': tile.move,
        'buff': tile.buff,
        'start': tile.start,
        'pawn_location': tile.pawn_location,
        'pawn_direction': tile.pawn_direction,
        'pawn_offset': tile.pawn_offset,
        'exits': []
    }
    for exit in tile.exits:
        doc['exits'].append(exit._id)
    return doc
