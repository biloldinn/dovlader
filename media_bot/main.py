import asyncio
import logging
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config.settings import settings
from media_bot.handlers import start, upload, list_media, search, admin
from media_bot.services.database import init_db

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE) if not settings.WEBHOOK_HOST else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot):
    await init_db()
    if settings.WEBHOOK_HOST:
        webhook_url = settings.WEBHOOK_URL
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_webhook(webhook_url)
        logger.info(f"Webhook o'rnatildi: {webhook_url}")
    else:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot Polling rejimida ishga tushmoqda...")

async def main():
    settings.setup_directories()
    
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=None)
    )
    dp = Dispatcher()
    
    # Register handlers
    dp.include_router(start.router)
    dp.include_router(upload.router)
    dp.include_router(list_media.router)
    dp.include_router(search.router)
    dp.include_router(admin.router)
    
    dp.startup.register(on_startup)

    if settings.WEBHOOK_HOST:
        # Webhook mode
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        logger.info(f"Starting webhook on {settings.WEBAPP_HOST}:{settings.WEBAPP_PORT}")
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, settings.WEBAPP_HOST, settings.WEBAPP_PORT)
        await site.start()
        
        # Keep running
        await asyncio.Event().wait()
    else:
        # Polling mode
        await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
