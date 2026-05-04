import logging
import sys
import threading

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
    force=True,
)

from loader import dp
from aiogram import executor
from handlers.users.web_server import start_web_server
from utils.set_bot_commands import set_default_commands
from utils.notify_admins import on_startup_notify

log = logging.getLogger("oxus_bot.app")


async def on_startup(dispatcher):
    log.info("on_startup: setting default commands")
    await set_default_commands(dispatcher)
    log.info("on_startup: notifying admins")
    await on_startup_notify(dispatcher)
    log.info("on_startup: done")


if __name__ == '__main__':
    log.info("starting web server thread on background")
    web_server_thread = threading.Thread(target=start_web_server, daemon=True)
    web_server_thread.start()
    log.info("starting bot polling")
    executor.start_polling(dp, on_startup=on_startup)
