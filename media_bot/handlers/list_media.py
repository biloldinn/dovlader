from aiogram import Router, types, F
from aiogram.filters import Command
from media_bot.repositories.base import MediaRepository

router = Router()

@router.message(Command("list"))
async def cmd_list(message: types.Message):
    media_list = await MediaRepository.get_user_media(message.from_user.id)
    
    if not media_list:
        return await message.answer("Sizda hali yuklab olingan media yo'q.")
        
    response = "Sizning oxirgi yuklamalaringiz:\n\n"
    for m in media_list:
        response += f"📄 {m.file_name} ({m.file_type})\n"
        
    await message.answer(response)
