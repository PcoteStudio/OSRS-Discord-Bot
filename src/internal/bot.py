import datetime
import logging
import nextcord
from nextcord.ext import commands
from pathlib import Path


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=self.get_prefix_,
            description=kwargs.pop('description'),
            intents=kwargs.pop('intents')
        )
        self.start_time = None
        self.app_info = None

        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())

    async def track_start(self):
        await self.wait_until_ready()
        self.start_time = datetime.datetime.utcnow()

    async def get_prefix_(self, bot, message):
        prefix = [bot.config['BOT_PREFIX']]
        return commands.when_mentioned_or(*prefix)(bot, message)

    async def load_all_extensions(self):
        cogs = [x.stem for x in Path('cogs').glob('*.py')]
        for extension in cogs:
            try:
                self.load_extension(f'cogs.{extension}')
                logging.info(f'Loaded {extension}')
            except Exception as e:
                error = f'{extension}\n {type(e).__name__} : {e}'
                logging.error(f'Failed to load extension {error}')
        # self.load_extension('onami')

    async def on_ready(self):
        self.app_info = await self.application_info()
        logging.info(f'Using nextcord version: {nextcord.__version__}')
        logging.info(f'Logged in as: {self.user.name}')
        logging.info(f'Owner: {self.app_info.owner}')

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)