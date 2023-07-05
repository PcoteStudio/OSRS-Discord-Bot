import logging
from internal.databasemanager import instance
from pymongo import UpdateOne
from collections.abc import Iterable

from internal.util.emoji import Emoji


async def get_emoji_by_id(emoji_id: int):
    doc = await instance.emoji.find_one({'_id': emoji_id})
    if doc is None:
        return None
    return doc_to_emoji(doc)


async def insert(emoji: Emoji):
    doc = emoji_to_doc(emoji)
    result = await instance.emoji.insert_one(doc)
    logging.info(f"Emoji inserted (_id:{emoji.emoji_id}, name:{emoji.emoji_string})")
    return result


async def insert_many(emojis: Iterable[Emoji]):
    docs = []
    for emoji in emojis:
        doc = emoji_to_doc(emoji)
        docs.append(doc)

    result = await instance.emoji.insert_many(docs)
    logging.info(f"Multiple emojis inserted (len:{len(docs)})")
    return result


async def update(emoji: Emoji):
    result = await instance.emoji.update_one({'_id': emoji.emoji_id}, {'$set': emoji_to_doc(emoji)})
    logging.info(f"Emoji updated (_id:{emoji.emoji_id}, name:{emoji.emoji_string})")
    return result


async def update_many(emojis: Iterable[Emoji]):
    requests = []
    for emoji in emojis:
        r = UpdateOne({"_id": emoji.emoji_id}, {'$set': emoji_to_doc(emoji)})
        requests.append(r)
    if len(requests) > 0:
        result = await instance.emoji.bulk_write(requests, ordered=False)
        logging.info(f"Multiple emojis updated (len:{len(requests)})")
        return result


async def delete(emoji: Emoji):
    result = await instance.emoji.delete_one({'_id': emoji.emoji_id})
    logging.info(f"Emoji deleted (_id:{emoji.emoji_string}, name:{emoji.emoji_string})")
    return result


def emoji_to_doc(emoji: Emoji):
    return {
        '_id': emoji.emoji_id,
        'emoji_string': emoji.emoji_string,
        'animated': emoji.animated,
    }


def doc_to_emoji(doc):
    emoji = Emoji(doc['emoji_string'], doc['_id'], doc['animated'])
    return emoji
