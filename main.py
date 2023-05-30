import os
import nextcord
import logging
import asyncio
from internal.bot import Bot


def load_config():
    from os.path import join, dirname
    from dotenv import load_dotenv
    from internal import configmanager

    dotenv_path = join(dirname(__file__), '.env')
    if os.path.isfile(dotenv_path):
        load_dotenv(dotenv_path)

    configmanager.init('config.json', 'utf-8')
    configmanager.instance['PCOTE_MONGO_CONNECTION_STRING'] = os.environ['PCOTE_MONGO_CONNECTION_STRING']
    configmanager.instance['PCOTE_MONGO_DATABASE_NAME'] = os.environ['PCOTE_MONGO_DATABASE_NAME']
    configmanager.instance['PCOTE_BOT_TOKEN'] = os.environ['PCOTE_BOT_TOKEN']
    configmanager.instance['PCOTE_WOM_API_KEY'] = os.environ['PCOTE_WOM_API_KEY']
    return configmanager.instance


async def run():
    config = load_config()

    if config.get('DATABASE') is True:
        from internal import databasemanager
        databasemanager.init(config.get('PCOTE_MONGO_CONNECTION_STRING'),
                             config.get('PCOTE_MONGO_DATABASE_NAME'))

    intents = nextcord.Intents.default()
    intents.message_content = True
    bot = Bot(
        config=config,
        description=config.get('BOT_DESCRIPTION'),
        intents=intents
    )

    bot.config = config

    try:
        token = config.get('PCOTE_BOT_TOKEN')
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.logout()
        exit()

if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] [%(levelname)-4s] %(message)s',
                        level=logging.INFO, datefmt='%H:%M:%S')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
