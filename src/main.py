import os
import nextcord
import logging
import asyncio
from internal.bot import Bot


def load_config():
    from internal import configmanager

    configmanager.init(os.path.join(os.getcwd(), 'config/serverSettings.json'), 'utf-8')
    return configmanager.instance


async def run():
    config = load_config()
    is_prod = config.get('IS_PROD', False)

    if config.get('DATABASE') is True:
        from internal import databasemanager
        databasemanager.init(config.get('MONGO_CONNECTION_STRING'),
                             config.get('PROD_MONGO_DATABASE_NAME' if is_prod else 'MONGO_DATABASE_NAME'))

    intents = nextcord.Intents.default()
    intents.message_content = True
    bot = Bot(
        config=config,
        description=config.get('BOT_DESCRIPTION'),
        intents=intents
    )

    try:
        token = config.get('PROD_BOT_TOKEN' if is_prod else 'BOT_TOKEN')
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.logout()
        exit()


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] [%(levelname)-4s] %(message)s',
                        level=logging.INFO, datefmt='%H:%M:%S')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
