import os
import nextcord
import logging
import asyncio
from internal.bot import Bot


def load_config():
    from os.path import join, dirname
    from dotenv import dotenv_values
    from internal import configmanager

    dotenv_path = join(dirname(__file__), 'config/.env')
    env_config = dotenv_values(dotenv_path)

    configmanager.init('config/serverSettings.json', 'utf-8')
    configmanager.instance = {**configmanager.instance, **env_config}
    return configmanager.instance


async def run():
    config = load_config()

    if config.get('DATABASE') is True:
        from internal import databasemanager
        databasemanager.init(config.get('MONGO_CONNECTION_STRING'),
                             config.get('MONGO_DATABASE_NAME'))

    intents = nextcord.Intents.default()
    intents.message_content = True
    bot = Bot(
        config=config,
        description=config.get('BOT_DESCRIPTION'),
        intents=intents
    )

    bot.config = config

    try:
        token = config.get('BOT_TOKEN')
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.logout()
        exit()


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] [%(levelname)-4s] %(message)s',
                        level=logging.INFO, datefmt='%H:%M:%S')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
