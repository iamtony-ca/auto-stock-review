"""
Daily 반도체 / AI / Physical AI 종목 DART 공시 모니터링 엔트리포인트.

GitHub Actions cron 또는 로컬에서 직접 실행:
    python main.py
"""

import argparse
import datetime
import logging
import os
import sys

from config.watch_list import TARGET_KEYWORDS, get_all_companies
from core.dart_watcher import DartWatcher
from core.interfaces import DisclosureItem, LLMProcessor, Notifier
from core.llm import GeminiProcessor
from core.notifiers import ConsoleNotifier, MultiNotifier, SlackNotifier


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def build_notifier() -> Notifier:
    """환경변수 유무에 따라 사용할 알림 채널 조립."""
    channels: list[Notifier] = [ConsoleNotifier()]
    slack_url = os.getenv("SLACK_WEBHOOK_URL", "").strip()
    if slack_url:
        channels.append(SlackNotifier(webhook_url=slack_url))
    return MultiNotifier(channels)


def build_llm() -> LLMProcessor:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("GEMINI_API_KEY environment variable is required.")
    return GeminiProcessor(api_key=api_key)


def build_watcher() -> DartWatcher:
    api_key = os.getenv("DART_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("DART_API_KEY environment variable is required.")
    return DartWatcher(
        api_key=api_key,
        companies=get_all_companies(),
        keywords=TARGET_KEYWORDS,
    )


def format_header(items: list[DisclosureItem], target_date: datetime.date) -> str:
    return (
        f":zap: *[Daily 반도체 & Physical AI Brief] {target_date.isoformat()}*\n"
        f"감시 대상 {len(get_all_companies())}개 종목 중 *{len(items)}건*의 핵심 공시 발생."
    )


def format_empty_message(target_date: datetime.date) -> str:
    return (
        f":zap: *[Daily 반도체 & Physical AI Brief] {target_date.isoformat()}*\n"
        f"감시 대상 {len(get_all_companies())}개 종목에서 오늘의 핵심 키워드 공시는 없습니다."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DART 공시 일일 감시 봇")
    parser.add_argument(
        "--date",
        help="조회 기준일 (YYYY-MM-DD). 기본값: 오늘",
        default=None,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="알림 전송 없이 콘솔 출력만 수행",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument(
        "--quiet-when-empty",
        action="store_true",
        help="해당일 공시가 0건이면 알림을 보내지 않음",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    setup_logging(args.verbose)
    log = logging.getLogger("main")

    target_date = (
        datetime.date.fromisoformat(args.date) if args.date else datetime.date.today()
    )

    watcher = build_watcher()
    items = watcher.run(target_date)

    notifier = ConsoleNotifier() if args.dry_run else build_notifier()

    if not items:
        log.info("No target disclosures for %s.", target_date)
        if not args.quiet_when_empty:
            notifier.send(format_empty_message(target_date))
        return 0

    notifier.send(format_header(items, target_date))

    llm = build_llm()
    for item in items:
        summary = llm.summarize_disclosure(item)
        notifier.send(summary)

    log.info("Done. Processed %d disclosures.", len(items))
    return 0


if __name__ == "__main__":
    sys.exit(main())
