import asyncio
import logging

import handlers
from aiogram import Bot, Dispatcher

from config import load_config, LoggerConfig
from middlewares import AuthMiddleware
from services import Storage

logger = logging.getLogger(__name__)


def configurate_logger(config: LoggerConfig):
    logging.basicConfig(
        level=config.level,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    )


async def main():
    config = load_config('config.ini')

    logger.warning('Configurate logger')
    configurate_logger(config.logger)

    logger.warning('Initiate storage')
    storage = Storage.from_url(config.redis.url)

    logger.warning('Starting bot')
    bot = Bot(token=config.tgbot.token)

    dp = Dispatcher(storage=storage)
    dp.message.middleware(AuthMiddleware(storage=storage))
    dp.include_routers(
        handlers.echo_router,
    )

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning('Bot stopped!')
