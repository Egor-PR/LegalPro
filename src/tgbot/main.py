import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import load_config, LoggerConfig
from middlewares import AuthMiddleware
from services import Application, GoogleSheetsApiService, Storage
from services.repostiories import Repository
from handlers import messages_router

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

    logger.warning('Initiate google repository')
    google_repo = GoogleSheetsApiService(
        creds_file=config.google_sheets.creds_file,
        discovery_url=config.google_sheets.discovery_url,
        service_name=config.google_sheets.service_name,
        scopes=config.google_sheets.scopes,
        version=config.google_sheets.version,
    )

    logger.warning('Initiate repository')
    repository = Repository(storage=storage, google_sheet_service=google_repo)

    logger.warning('Create main app interface')
    app = Application(repository=repository)

    logger.warning('Starting bot')
    bot = Bot(token=config.tgbot.token)

    dp = Dispatcher(app=app)
    dp.message.middleware(AuthMiddleware(storage=storage))
    dp.include_routers(
        messages_router,
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
