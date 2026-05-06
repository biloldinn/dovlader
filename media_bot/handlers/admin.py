from aiogram import Router, types, F
from aiogram.filters import Command
from config.settings import settings

router = Router()

@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id not in settings.ADMIN_IDS:
        return # Ignore non-admins
        
    await message.answer(
        "Admin paneliga xush kelibsiz!\n\n"
        "Statistika: /stats\n"
        "Foydalanuvchini bloklash: /block <id>"
    )

@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if message.from_user.id not in settings.ADMIN_IDS:
        return
        
    # Basic stats could be added here
    await message.answer("Statistika hozircha mavjud emas.")
