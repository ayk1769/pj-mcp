"""アプリケーションの設定を管理するモジュール."""
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

# 環境変数の読み込み
config_path = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(dotenv_path=config_path)


class Settings(BaseModel):
    """アプリケーションの設定."""

    # Slack設定
    slack_bot_token: str = Field(..., env="SLACK_BOT_TOKEN")
    slack_channel_id: str = Field(..., env="SLACK_CHANNEL_ID")
    slack_daily_report_keyword: str = Field("#日報", env="SLACK_DAILY_REPORT_KEYWORD")

    # Notion設定
    notion_api_key: str = Field(..., env="NOTION_API_KEY")
    notion_database_id: str = Field(..., env="NOTION_DATABASE_ID")

    # アプリケーション設定
    log_level: str = Field("INFO", env="LOG_LEVEL")
    sync_interval_minutes: int = Field(60, env="SYNC_INTERVAL_MINUTES")

    class Config:
        """Pydantic設定."""

        env_file = str(config_path)
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


@lru_cache()
def get_settings() -> Settings:
    """設定のシングルトンインスタンスを取得する.

    Returns:
        Settings: 設定のインスタンス
    """
    try:
        return Settings()
    except ValidationError as e:
        print(f"設定の読み込みに失敗しました: {e}")
        raise
