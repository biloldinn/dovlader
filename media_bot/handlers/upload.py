from aiogram import Router, types, F
from media_bot.services.url_processor import URLProcessor
from media_bot.repositories.base import MediaRepository
from aiogram.types import FSInputFile
import os
import logging
import time

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text.regexp(r'^https?://'))
async def handle_url(message: types.Message):
    url = message.text
    
    if not URLProcessor.is_valid_url(url):
        return await message.answer("Xato: Noto'g'ri URL format.")
    
    status_msg = await message.answer("Media yuklanmoqda...")
    start_time = time.time()
    
    try:
        platform, method = URLProcessor.is_platform_url(url)
        
        # UI update for known platforms
        if platform:
            await status_msg.edit_text(f"{platform.capitalize()} dan yuklanmoqda...")
        
        if method == 'yt-dlp':
            result = await URLProcessor.download_with_ytdlp(url)
        else:
            result = await URLProcessor.download_direct(url)
            
        file_path, file_hash, file_size, media_type, ext, width, height = result
        
        # Save to DB
        await MediaRepository.save({
            "user_id": message.from_user.id,
            "file_hash": file_hash,
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "file_size": file_size,
            "file_type": media_type,
            "original_url": url
        })
        
        duration = round(time.time() - start_time, 1)
        caption = f"Tayyor!\nVaqt: {duration}s\nHajm: {round(file_size / (1024*1024), 2)} MB"
        
        if media_type == 'image':
            await message.reply_photo(FSInputFile(file_path), caption=caption)
        else:
            await message.reply_video(FSInputFile(file_path), caption=caption)
            
        await status_msg.delete()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        error_text = "Xatolik yuz berdi!\n\n"
        if "HTTP 404" in str(e):
            error_text += "Havola topilmadi yoki media yopiq (private)."
        elif "size" in str(e).lower():
            error_text += "Fayl hajmi juda katta (maks: 50MB)."
        else:
            error_text += "Iltimos, keyinroq qayta urinib ko'ring yoki boshqa havola yuboring."
            
        await status_msg.edit_text(error_text)
