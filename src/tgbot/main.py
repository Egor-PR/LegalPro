import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import load_config, LoggerConfig
from middlewares import AuthMiddleware
from services import Application, GoogleSheetsApiService, Storage
from services.notifier import AbstractNotifier, TelegramBotNotifier
from services.repostiories import Repository, GoogleRepository
from handlers import commands_router, messages_router, BotCommands

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
    google_sheets_service = GoogleSheetsApiService(
        creds_file=config.google_sheets.creds_file,
        discovery_url=config.google_sheets.discovery_url,
        service_name=config.google_sheets.service_name,
        scopes=[config.google_sheets.scopes],
        version=config.google_sheets.version,
    )

    logger.warning('Initiate google repository')
    google_repository = GoogleRepository(
        storage=storage,
        google_sheet_service=google_sheets_service,
        spreadsheet_id=config.google_repository.spreadsheet_id,
        users_sheet_name=config.google_repository.users_sheet_name,
        users_sheet_range=config.google_repository.users_sheet_range,
        handbook_expire_seconds=config.google_repository.handbook_expire_seconds,
        work_types_sheet_name=config.google_repository.work_types_sheet_name,
        work_types_sheet_range=config.google_repository.work_types_sheet_range,
        clients_sheet_name=config.google_repository.clients_sheet_name,
        clients_sheet_range=config.google_repository.clients_sheet_range,
        work_time_report_sheet_name=config.google_repository.work_time_report_sheet_name,
        work_time_report_sheet_range=config.google_repository.work_time_report_sheet_range,
        work_time_report_remove_col=config.google_repository.work_time_report_remove_col,
        wtrs_sheet_name=config.google_repository.wtrs_sheet_name,
        wtrs_sheet_range=config.google_repository.wtrs_sheet_range,
        wtrs_date_from_cell=config.google_repository.wtrs_date_from_cell,
        wtrs_date_to_cell=config.google_repository.wtrs_date_to_cell,
        wtrs_user_cell=config.google_repository.wtrs_user_cell,
        wtrs_client_cell=config.google_repository.wtrs_client_cell,
        wtrs_time_plan_cell=config.google_repository.wtrs_time_plan_cell,
        wtrs_time_fact_cell=config.google_repository.wtrs_time_fact_cell,
        wtrs_time_net_cell=config.google_repository.wtrs_time_net_cell,
    )

    logger.warning('Initiate repository')
    repository = Repository(
        storage=storage,
        google_sheet_service=google_sheets_service,
        google_repository=google_repository,
    )

    logger.warning('Starting bot')
    bot = Bot(token=config.tgbot.token)

    logger.warning(f'Set bot commands')
    result = bot.set_my_commands(BotCommands.get_list())
    if not result:
        logger.error('Can`t set bot commands!')
        return

    logger.warning('Initiate notifier')
    notifier: AbstractNotifier = TelegramBotNotifier(bot=bot)

    logger.warning('Create main app interface')
    app = Application(repository=repository, notifier=notifier)

    dp = Dispatcher(app=app)
    dp.message.middleware(AuthMiddleware(storage=storage))
    dp.callback_query.middleware(AuthMiddleware(storage=storage))
    dp.include_routers(
        commands_router,
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
