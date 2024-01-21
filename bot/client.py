import os
from typing import Union
from pyromod import listen
from pyrogram import Client as RawClient
from pyrogram.storage import Storage
from configs import Config
from aiohttp import web
from bot.route import web_server

LOGGER = Config.LOGGER
log = LOGGER.getLogger(__name__)

class Client(RawClient):
    """ Custom Bot Class """

    def __init__(self, session_name: Union[str, Storage] = "RenameBot"):
        super().__init__(
            session_name,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(
                root="bot/plugins"
            )
        )

    async def start(self):
        await super().start()
        if not os.path.isdir(Config.DOWNLOAD_DIR):
            os.makedirs(Config.DOWNLOAD_DIR)
        if Config.WEBHOOK:
            app = web.AppRunner(await web_server())
            await app.setup()       
            await web.TCPSite(app, "0.0.0.0", 8080).start()
        log.info("Bot Started!")

    async def stop(self, *args):
        await super().stop()
        log.info("Bot Stopped!")
