from aiogram import Router, types, F
from aiogram.filters import CommandStart
from media_bot.repositories.base import UserRepository
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await UserRepository.get_or_create(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Yordam", callback_data="help"))
    
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}!\n\n"
        "Men ijtimoiy tarmoqlardan (YouTube, Instagram, TikTok) media yuklab beruvchi professional botman.\n\n"
        "Menga shunchaki havola (link) yuboring!",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data == "help")
async def help_callback(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Botdan qanday foydalanish kerak?\n\n"
        "1. Xohlagan ijtimoiy tarmoqdan havola yuboring.\n"
        "2. Men esa uni qayta ishlab, sizga yuboraman.\n\n"
        "Maksimal hajm: 50MB",
        reply_markup=callback.message.reply_markup
    )
