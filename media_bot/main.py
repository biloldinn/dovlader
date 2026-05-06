import asyncio
import logging
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config.settings import settings
from media_bot.handlers import start, upload, list_media, search, admin
from media_bot.services.database import init_db

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    # Ensure directories exist
    settings.setup_directories()
    
    # Initialize database
    await init_db()
    
    # Create bot and dispatcher
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
    
    # Start polling
    logger.info("Bot professional versiyada ishga tushdi!")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
