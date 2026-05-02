import threading
from loader import dp
from aiogram import executor
from handlers.users.web_server import start_web_server
from utils.set_bot_commands import set_default_commands
from utils.notify_admins import on_startup_notify


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    web_server_thread = threading.Thread(target=start_web_server)
    web_server_thread.start()
    executor.start_polling(dp, on_startup=on_startup)
