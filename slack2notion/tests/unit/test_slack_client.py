"""SlackClientモジュールのテスト."""
from unittest import TestCase, mock

from slack_sdk.errors import SlackApiError

from slack2notion.slack_client import SlackClient


class TestSlackClient(TestCase):
    """SlackClientのテストケース."""

    @mock.patch("slack2notion.slack_client.WebClient")
    @mock.patch("slack2notion.slack_client.get_settings")
    def test_initialization(self, mock_get_settings, mock_web_client) -> None:
        """SlackClientが正しく初期化されるかテスト."""
        # 設定のモック
        mock_settings = mock.MagicMock()
        mock_settings.slack_bot_token = "xoxb-test-token"
        mock_settings.slack_channel_id = "C12345678"
        mock_settings.slack_daily_report_keyword = "#日報"
        mock_get_settings.return_value = mock_settings
        
        # クライアントの初期化
        slack_client = SlackClient()
        
        # WebClientが正しいトークンで初期化されたか確認
        mock_web_client.assert_called_once_with(token="xoxb-test-token")
        
        # 属性が正しく設定されたか確認
        self.assertEqual(slack_client.channel_id, "C12345678")
        self.assertEqual(slack_client.daily_report_keyword, "#日報")

    @mock.patch("slack2notion.slack_client.WebClient")
    @mock.patch("slack2notion.slack_client.get_settings")
    def test_get_daily_reports(self, mock_get_settings, mock_web_client) -> None:
        """日報メッセージの取得が正しく行われるかテスト."""
        # 設定のモック
        mock_settings = mock.MagicMock()
        mock_settings.slack_bot_token = "xoxb-test-token"
        mock_settings.slack_channel_id = "C12345678"
        mock_settings.slack_daily_report_keyword = "#日報"
        mock_get_settings.return_value = mock_settings
        
        # WebClientのモック
        mock_client = mock.MagicMock()
        mock_web_client.return_value = mock_client
        
        # conversations_historyの返り値を設定
        mock_client.conversations_history.return_value = {
            "ok": True,
            "messages": [
                {"text": "これは#日報です。今日の作業内容...", "user": "U123", "ts": "1617267000.000100"},
                {"text": "通常のメッセージ", "user": "U456", "ts": "1617267100.000200"},
                {"text": "#日報 別の日報", "user": "U789", "ts": "1617267200.000300"},
            ]
        }
        
        # SlackClientのインスタンス化
        slack_client = SlackClient()
        
        # 日報メッセージの取得
        daily_reports = slack_client.get_daily_reports(days_ago=1)
        
        # 正しく日報メッセージがフィルタリングされたか確認
        self.assertEqual(len(daily_reports), 2)
        self.assertEqual(daily_reports[0]["text"], "これは#日報です。今日の作業内容...")
        self.assertEqual(daily_reports[1]["text"], "#日報 別の日報")
        
        # APIが正しく呼び出されたか確認
        mock_client.conversations_history.assert_called_once()
        call_args = mock_client.conversations_history.call_args[1]
        self.assertEqual(call_args["channel"], "C12345678")
        self.assertIn("oldest", call_args)  # タイムスタンプの確認

    @mock.patch("slack2notion.slack_client.WebClient")
    @mock.patch("slack2notion.slack_client.get_settings")
    def test_get_daily_reports_api_error(self, mock_get_settings, mock_web_client) -> None:
        """API呼び出しでエラーが発生した場合の挙動をテスト."""
        # 設定のモック
        mock_settings = mock.MagicMock()
        mock_get_settings.return_value = mock_settings
        
        # WebClientのモック
        mock_client = mock.MagicMock()
        mock_web_client.return_value = mock_client
        
        # APIエラーをシミュレート
        mock_client.conversations_history.side_effect = SlackApiError(
            "Error", {"ok": False, "error": "channel_not_found"}
        )
        
        # SlackClientのインスタンス化
        slack_client = SlackClient()
        
        # 日報メッセージの取得（エラーが発生するが、空のリストが返されるはず）
        daily_reports = slack_client.get_daily_reports(days_ago=1)
        
        # 空のリストが返されることを確認
        self.assertEqual(daily_reports, [])
