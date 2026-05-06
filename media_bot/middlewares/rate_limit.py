from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
import time
from collections import defaultdict
from config.settings import settings

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self):
        self.requests: Dict[int, list] = defaultdict(list)
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)
            
        user_id = event.from_user.id
        now = time.time()
        
        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < settings.RATE_LIMIT_WINDOW
        ]
        
        # Check limit
        if len(self.requests[user_id]) >= settings.RATE_LIMIT_PER_USER:
            await event.answer(
                f"⏳ Juda koʻp soʻrov. Iltimos, {settings.RATE_LIMIT_WINDOW} soniya kuting."
            )
            return
        
        self.requests[user_id].append(now)
        return await handler(event, data)
