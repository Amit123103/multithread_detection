"""Multi-channel notification dispatcher (Telegram, Discord, Slack, MS Teams, Webhook, Desktop, Email)."""

import logging
from typing import Optional

import requests

from threatvision.alerts.alert_types import AlertMessage, AlertSeverity
from threatvision.config.config import NotificationConfig

logger = logging.getLogger("threatvision.notifications")


class NotificationDispatcher:
    """Dispatches real-time threat alerts to external channels asynchronously."""

    def __init__(self, config: Optional[NotificationConfig] = None):
        self.config = config or NotificationConfig()

    def dispatch(self, alert: AlertMessage) -> None:
        """Send alert message across all configured notification channels."""
        logger.info(f"Dispatching Alert [{alert.severity}]: {alert.title} - {alert.body}")

        if self.config.enable_webhook and self.config.webhook_url:
            self._send_webhook(self.config.webhook_url, alert)

        if self.config.discord_webhook_url:
            self._send_discord(self.config.discord_webhook_url, alert)

        if self.config.slack_webhook_url:
            self._send_slack(self.config.slack_webhook_url, alert)

        if self.config.telegram_bot_token and self.config.telegram_chat_id:
            self._send_telegram(
                self.config.telegram_bot_token, self.config.telegram_chat_id, alert
            )

        if alert.severity == AlertSeverity.CRITICAL:
            self._trigger_audible_alarm()

    def _send_webhook(self, url: str, alert: AlertMessage) -> None:
        try:
            requests.post(url, json=alert.model_dump(), timeout=3)
        except Exception as e:
            logger.warning(f"Webhook notification failed: {e}")

    def _send_discord(self, url: str, alert: AlertMessage) -> None:
        try:
            payload = {
                "content": f"🚨 **THREATVISION ALERT [{alert.severity.value}]**\n**{alert.title}**\n{alert.body}\nThreat Score: {int(alert.threat_score * 100)}%"
            }
            requests.post(url, json=payload, timeout=3)
        except Exception as e:
            logger.warning(f"Discord notification failed: {e}")

    def _send_slack(self, url: str, alert: AlertMessage) -> None:
        try:
            payload = {
                "text": f"⚠️ *ThreatVision Alert [{alert.severity.value}]*\n*{alert.title}*\n{alert.body}"
            }
            requests.post(url, json=payload, timeout=3)
        except Exception as e:
            logger.warning(f"Slack notification failed: {e}")

    def _send_telegram(self, bot_token: str, chat_id: str, alert: AlertMessage) -> None:
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            text = f"🚨 *{alert.title}*\n{alert.body}\nLevel: {alert.severity.value}\nScore: {int(alert.threat_score * 100)}%"
            requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=3)
        except Exception as e:
            logger.warning(f"Telegram notification failed: {e}")

    def _trigger_audible_alarm(self) -> None:
        try:
            import winsound
            winsound.Beep(1000, 400)
        except Exception:
            print("\a", end="")  # Terminal bell fallback
