import os
import re

import aiohttp
import aiofiles


class Emoji:
    def __init__(self, emoji_string: str, emoji_id: str = None, animated: bool = None):
        self.emoji_string = emoji_string
        self.emoji_id = emoji_id
        self.animated = animated

    @classmethod
    async def load_emoji(cls, emoji_string):
        if not emoji_string.startswith('<'):
            return cls(emoji_string)

        parsed_emoji_string = re.search(r"<(a?)(:\w*:)(\d*)>", emoji_string)
        emoji_id = parsed_emoji_string.group(3)

        emoji = await find_emoji(emoji_id)
        if not emoji:
            animated = True if parsed_emoji_string.group(1) else False
            emoji_string = parsed_emoji_string.group(2)
            emoji = await create_emoji(emoji_string, emoji_id, animated)

        return emoji


from database import emojidb


def build_url(emoji_id, image_extension):
    # 'https://cdn.discordapp.com/emojis/1062676457341599775.webp?size=96&quality=lossless'
    base = 'https://cdn.discordapp.com/emojis/'
    return base + emoji_id + "." + image_extension


async def fetch_image(emoji_id, animated):
    image_extension = 'webp'  # 'gif' if animated else 'webp'
    image_url = build_url(emoji_id, image_extension)

    path_image = os.path.join(os.getcwd() + f"/src/memoji/{emoji_id}.{image_extension}")
    os.makedirs(os.path.dirname(path_image), exist_ok=True)

    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as res:
            if res.status != 200:
                print(f"Download failed: {res.status}")
                return

            content = await res.read()

            async with aiofiles.open(path_image, "+wb") as f:
                await f.write(content)


async def find_emoji(emoji_id):
    emoji = await emojidb.get_emoji_by_id(emoji_id)
    return emoji


async def create_emoji(emoji_string, emoji_id, animated):
    emoji = Emoji(emoji_string, emoji_id, animated)
    await fetch_image(emoji.emoji_id, emoji.animated)
    await emojidb.insert(emoji)

    return emoji
