import aiohttp
import aiofiles
import hashlib
import os
import re
import asyncio
from urllib.parse import urlparse
from yt_dlp import YoutubeDL
from PIL import Image
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class URLProcessor:
    @staticmethod
    def is_valid_url(url: str) -> bool:
        regex = re.compile(
            r'^(?:http|ftp|https)://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None
    
    @staticmethod
    def is_platform_url(url: str) -> tuple:
        platforms = {
            'youtube.com': ('youtube', 'yt-dlp'),
            'youtu.be': ('youtube', 'yt-dlp'),
            'instagram.com': ('instagram', 'yt-dlp'),
            'tiktok.com': ('tiktok', 'yt-dlp'),
            'twitter.com': ('twitter', 'yt-dlp'),
            'facebook.com': ('facebook', 'yt-dlp'),
            'vimeo.com': ('vimeo', 'yt-dlp'),
        }
        for domain, info in platforms.items():
            if domain in url.lower():
                return info
        return (None, None)
    
    @staticmethod
    async def download_with_ytdlp(url: str) -> tuple:
        """Returns (file_path, file_hash, file_size, media_type, extension, width, height)"""
        ydl_opts = {
            'outtmpl': os.path.join(settings.MEDIA_DIR, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: _download(ydl_opts, url))
        return result
    
    @staticmethod
    async def download_direct(url: str) -> tuple:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            async with session.get(url, headers=headers, timeout=30) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                content_type = response.headers.get('content-type', '')
                if not ('image' in content_type or 'video' in content_type):
                    raise Exception("URL media (rasm/video) emas")
                
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > settings.MAX_FILE_SIZE_BYTES:
                    raise Exception(f"Fayl hajmi {settings.MAX_FILE_SIZE_MB} MB dan katta")
                
                data = await response.read()
                
                if len(data) > settings.MAX_FILE_SIZE_BYTES:
                    raise Exception(f"Fayl hajmi chegaradan katta")
                
                # Hash
                file_hash = hashlib.sha256(data).hexdigest()
                
                # Extension
                ext = URLProcessor._get_extension(content_type, url)
                
                # Filename
                file_name = f"{file_hash[:16]}{ext}"
                file_path = os.path.join(settings.MEDIA_DIR, file_name)
                
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(data)
                
                media_type = 'image' if 'image' in content_type else 'video'
                
                # Get dimensions for images
                width, height = None, None
                if media_type == 'image':
                    try:
                        with Image.open(file_path) as img:
                            width, height = img.size
                    except:
                        pass
                
                return file_path, file_hash, len(data), media_type, ext, width, height

    @staticmethod
    def _get_extension(content_type: str, url: str) -> str:
        # Simple extension extractor
        if 'image/jpeg' in content_type: return '.jpg'
        if 'image/png' in content_type: return '.png'
        if 'image/gif' in content_type: return '.gif'
        if 'video/mp4' in content_type: return '.mp4'
        
        path = urlparse(url).path
        ext = os.path.splitext(path)[1]
        return ext if ext else '.bin'

def _download(ydl_opts, url):
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            ext = os.path.splitext(file_path)[1]
            
            if not os.path.exists(file_path):
                # Handle cases where extension might change
                base_path = os.path.splitext(file_path)[0]
                for f in os.listdir(os.path.dirname(file_path)):
                    if f.startswith(os.path.basename(base_path)):
                        file_path = os.path.join(os.path.dirname(file_path), f)
                        ext = os.path.splitext(f)[1]
                        break
            
            with open(file_path, 'rb') as f:
                data = f.read()
                file_hash = hashlib.sha256(data).hexdigest()
                file_size = len(data)
            
            # More robust media type detection
            media_type = 'video' if (info.get('duration') or info.get('vcodec') != 'none') else 'image'
            
            return file_path, file_hash, file_size, media_type, ext, info.get('width'), info.get('height')
    except Exception as e:
        logger.error(f"ytdlp error: {e}")
        raise e
