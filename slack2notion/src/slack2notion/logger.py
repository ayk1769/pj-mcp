"""ロギング設定を管理するモジュール."""
import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from slack2notion.config import get_settings


def setup_logger(log_file: Optional[Path] = None) -> None:
    """アプリケーションのロガーを設定する.

    Args:
        log_file: ログファイルのパス（オプション）
    """
    settings = get_settings()
    log_level = settings.log_level

    # ロガーの初期化
    logger.remove()

    # 標準出力へのログ
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
    )

    # ファイルへのログ（指定された場合）
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(log_file),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation="10 MB",
            compression="zip",
            retention="30 days",
        )

    logger.info(f"ロガーの設定が完了しました。レベル: {log_level}")
