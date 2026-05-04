import logging
import traceback

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.errors_handler()
async def global_error_handler(update, exception):
    logging.error(
        "Unhandled handler error: %s\nUpdate: %s\n%s",
        exception, update, traceback.format_exc(),
    )
    return True
