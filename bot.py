import asyncio
import motor.motor_asyncio as aiomongo

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, Message

from handlers import (
    user_registration,
    user_reg_launching,
    commands_handler,
    admin_session,
)
from handlers.main_kb_handlers import (
    main_bot_keyboard_handler,
    profile_check_switch_handler,
)
from filters import profile_fetching_filters
from database_actions import Database
from keyboards.fabric import UsersContainer

from middlewares import AntiFloodMiddleware
from bot_data.bot_commands_list import BOT_COMMANDS
from config_reader import config


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command=command, description=description)
        for command, description in BOT_COMMANDS.items()
    ]
    await bot.set_my_commands(main_menu_commands)


async def main():
    bot = Bot(config.BOT_TOKEN.get_secret_value())
    dp = Dispatcher()

    await set_main_menu(bot)

    dp.message.middleware(AntiFloodMiddleware())

    dp.include_routers(
        commands_handler.router,
        user_registration.router,
        user_reg_launching.router,
        main_bot_keyboard_handler.router,
        profile_check_switch_handler.router,
        profile_fetching_filters.router,
        admin_session.router,
    )

    db_client = aiomongo.AsyncIOMotorClient(config.DATABASE_URL.get_secret_value())
    database = Database(db_client)
    users_container = UsersContainer()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, _db=database, _users_to_check=users_container)


if __name__ == "__main__":
    asyncio.run(main())
