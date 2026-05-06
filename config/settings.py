import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Set, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / "config" / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Bot
    BOT_TOKEN: str
    BOT_USERNAME: str = "MediaUploadBot"
    
    # Database
    DATABASE_URL: str = "sqlite:///media_bot.db"
    
    # Storage
    STORAGE_TYPE: str = "local"
    MEDIA_DIR: Path = BASE_DIR / "media"
    MAX_FILE_SIZE_MB: int = 50
    
    @property
    def MAX_FILE_SIZE_BYTES(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    # Security
    ADMIN_IDS: Any = []
    
    # Extensions
    ALLOWED_EXTENSIONS: Any = {"jpg", "jpeg", "png", "gif", "webp", "mp4", "avi", "mov", "mkv", "webm"}
    
    @field_validator("ADMIN_IDS", "ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_comma_separated(cls, v: Any) -> Any:
        if isinstance(v, str):
            items = [x.strip() for x in v.split(",") if x.strip()]
            # If it's ADMIN_IDS, convert to int
            # We can't easily distinguish field here without more logic, 
            # so let's use separate validators or check if items are digits.
            return items
        return v

    @field_validator("ADMIN_IDS", mode="after")
    @classmethod
    def convert_admin_ids_to_int(cls, v: Any) -> List[int]:
        if isinstance(v, list):
            return [int(x) for x in v if str(x).isdigit()]
        return v

    @field_validator("ALLOWED_EXTENSIONS", mode="after")
    @classmethod
    def convert_to_set(cls, v: Any) -> Set[str]:
        if isinstance(v, list):
            return set(v)
        return v
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Path = BASE_DIR / "logs" / "bot.log"
    
    # Webhook
    WEBHOOK_HOST: Optional[str] = os.getenv("WEBHOOK_HOST")
    WEBHOOK_PATH: str = "/webhook"
    WEBAPP_HOST: str = "0.0.0.0"
    WEBAPP_PORT: int = int(os.getenv("PORT", 8000))
    
    @property
    def WEBHOOK_URL(self) -> Optional[str]:
        if self.WEBHOOK_HOST:
            return f"{self.WEBHOOK_HOST}{self.WEBHOOK_PATH}"
        return None

    def setup_directories(self):
        self.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.setup_directories()
