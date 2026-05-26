"""
알림 채널 구현체.

ConsoleNotifier  - 로컬 디버깅용
SlackNotifier    - Slack Incoming Webhook
(추후 추가 예정: TelegramNotifier, EmailNotifier, NotionNotifier)
"""

import json
import logging

import requests

from core.interfaces import Notifier

logger = logging.getLogger(__name__)


class ConsoleNotifier(Notifier):
    def send(self, message: str) -> bool:
        print("\n" + "=" * 60)
        print(message)
        print("=" * 60 + "\n")
        return True


class SlackNotifier(Notifier):
    """Slack Incoming Webhook 기반 알림."""

    def __init__(self, webhook_url: str, timeout: int = 10):
        self.webhook_url = webhook_url
        self.timeout = timeout

    def send(self, message: str) -> bool:
        if not self.webhook_url:
            logger.warning("SlackNotifier: webhook_url is empty, skipping.")
            return False

        payload = {"text": message, "mrkdwn": True}
        try:
            res = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
            )
            if res.status_code == 200 and res.text == "ok":
                return True
            logger.error(
                "Slack webhook returned %s: %s", res.status_code, res.text
            )
            return False
        except requests.RequestException as e:
            logger.error("Slack webhook network error: %s", e)
            return False


class MultiNotifier(Notifier):
    """여러 채널에 동시 브로드캐스트하는 컴포지트 노티파이어."""

    def __init__(self, notifiers: list[Notifier]):
        self.notifiers = notifiers

    def send(self, message: str) -> bool:
        results = []
        for n in self.notifiers:
            ok = n.send(message)
            if not ok:
                logger.warning("Notifier %s failed to send.", n.name)
            results.append(ok)
        return all(results)
