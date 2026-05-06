from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject
from media_bot.repositories.base import MediaRepository

router = Router()

@router.message(Command("search"))
async def cmd_search(message: types.Message, command: CommandObject):
    if not command.args:
        return await message.answer("Qidirish uchun matn yuboring: /search <matn>")
        
    query = command.args
    results = await MediaRepository.search(message.from_user.id, query)
    
    if not results:
        return await message.answer(f"'{query}' bo'yicha hech narsa topilmadi.")
        
    response = f"Qidiruv natijalari ('{query}'):\n\n"
    for r in results:
        response += f"🔍 {r.file_name}\n"
        
    await message.answer(response)
