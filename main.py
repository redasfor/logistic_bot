import asyncio
from aiogram import Bot, Dispatcher
from config import settings
from app.handlers import user_handlers, admin_handlers
from aiogram.fsm.storage.redis import RedisStorage, Redis
from aiogram.types import BotCommand
import logging


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command="/start", description="Старт бота"),
    ]

    await bot.set_my_commands(main_menu_commands)


async def main() -> None:
    redis = await Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    storage = RedisStorage(redis=redis)

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] #%(levelname)-8s %(filename)s:"
        "%(lineno)d - %(name)s - %(message)s",
    )
    logger.info("Starting bot")

    bot = Bot(token=settings.TOKEN.get_secret_value())
    dp = Dispatcher(storage=storage)
    dp.startup.register(set_main_menu)

    dp.include_router(admin_handlers.admin_router)
    dp.include_router(user_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
