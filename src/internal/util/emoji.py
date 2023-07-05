import os
import re

import aiohttp
import aiofiles


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

class Emoji:
    def __init__(self, emoji_string: str):
        if not emoji_string.startswith('<'):
            self.is_custom = False
            self.emoji_id = emoji_string
            return

        self.is_custom = True

        result = re.search(r"<(a?)(:\w*:)(\d*)>", emoji_string)

        self.animated = True if result.group(1) else False
        self.emoji_string = result.group(2)
        self.emoji_id = result.group(3)

    @classmethod
    async def create_emoji(cls, emoji_string):
        self = cls(emoji_string)

        await fetch_image(self.emoji_id, self.animated)
