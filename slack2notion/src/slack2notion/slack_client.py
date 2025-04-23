"""Slack APIとのインタラクションを管理するモジュール."""
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from loguru import logger
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from slack2notion.config import get_settings


class SlackClient:
    """Slack APIとのインタラクションを管理するクラス."""

    def __init__(self) -> None:
        """SlackClientの初期化."""
        settings = get_settings()
        self.client = WebClient(token=settings.slack_bot_token)
        self.channel_id = settings.slack_channel_id
        self.daily_report_keyword = settings.slack_daily_report_keyword
        logger.info(f"SlackClient初期化: チャンネルID={self.channel_id}")

    def get_daily_reports(
        self, days_ago: int = 1, oldest_timestamp: Optional[str] = None
    ) -> List[Dict]:
        """指定された期間内の日報メッセージを取得する.

        Args:
            days_ago: 何日前までのメッセージを取得するか
            oldest_timestamp: 取得開始タイムスタンプ（指定されている場合）

        Returns:
            List[Dict]: 日報メッセージのリスト
        """
        try:
            # タイムスタンプの計算
            if oldest_timestamp is None:
                oldest_time = datetime.now() - timedelta(days=days_ago)
                oldest_timestamp = str(int(oldest_time.timestamp()))

            logger.info(f"{days_ago}日前からのメッセージを取得します。")

            # メッセージの取得
            response = self.client.conversations_history(
                channel=self.channel_id, oldest=oldest_timestamp
            )

            # 日報メッセージのフィルタリング
            daily_reports = []
            if response["ok"]:
                messages = response["messages"]
                for message in messages:
                    if (
                        "text" in message
                        and self.daily_report_keyword in message["text"]
                    ):
                        logger.debug(f"日報メッセージを見つけました: {message['text'][:50]}...")
                        daily_reports.append(message)

            logger.info(f"日報メッセージを{len(daily_reports)}件取得しました")
            return daily_reports

        except SlackApiError as e:
            logger.error(f"Slack API エラー: {e.response['error']}")
            return []

    def get_thread_replies(self, thread_ts: str) -> List[Dict]:
        """スレッドの返信を取得する.

        Args:
            thread_ts: スレッドのタイムスタンプ

        Returns:
            List[Dict]: スレッド内の返信メッセージのリスト
        """
        try:
            response = self.client.conversations_replies(
                channel=self.channel_id, ts=thread_ts
            )
            if response["ok"] and len(response["messages"]) > 1:
                # 最初のメッセージはスレッドの親なので除外
                return response["messages"][1:]
            return []
        except SlackApiError as e:
            logger.error(f"スレッド返信の取得エラー: {e.response['error']}")
            return []

    def get_user_info(self, user_id: str) -> Dict:
        """ユーザー情報を取得する.

        Args:
            user_id: SlackのユーザーID

        Returns:
            Dict: ユーザー情報
        """
        try:
            response = self.client.users_info(user=user_id)
            if response["ok"]:
                return response["user"]
            return {}
        except SlackApiError as e:
            logger.error(f"ユーザー情報取得エラー: {e.response['error']}")
            return {}
