"""
DART (전자공시시스템) Open API 클라이언트.

오늘 발행된 공시 중 감시 대상 기업의 핵심 키워드 공시만 필터링한다.
"""

import datetime
import logging

import requests

from config.watch_list import get_company_sector
from core.interfaces import DisclosureItem

logger = logging.getLogger(__name__)

DART_LIST_URL = "https://opendart.fss.or.kr/api/list.json"


class DartWatcher:
    def __init__(
        self,
        api_key: str,
        companies: list[str],
        keywords: list[str],
        page_count: int = 100,
    ):
        if not api_key:
            raise ValueError("DART API key is required")
        self.api_key = api_key
        self.companies = set(companies)
        self.keywords = keywords
        self.page_count = page_count

    def fetch_notices(self, target_date: datetime.date | None = None) -> list[dict]:
        """지정된 날짜(기본: 오늘)에 발행된 공시 전체 페이지를 수집."""
        target_date = target_date or datetime.date.today()
        date_str = target_date.strftime("%Y%m%d")

        notices: list[dict] = []
        page_no = 1
        while True:
            params = {
                "crtfc_key": self.api_key,
                "bgn_de": date_str,
                "end_de": date_str,
                "page_count": str(self.page_count),
                "page_no": str(page_no),
            }
            try:
                res = requests.get(DART_LIST_URL, params=params, timeout=15)
                res.raise_for_status()
                data = res.json()
            except requests.RequestException as e:
                logger.error("DART API request failed: %s", e)
                break

            status = data.get("status")
            if status == "013":
                logger.info("No disclosures found for %s.", date_str)
                break
            if status != "000":
                logger.error("DART API error: %s - %s", status, data.get("message"))
                break

            page_list = data.get("list", [])
            notices.extend(page_list)

            total_page = int(data.get("total_page", 1))
            if page_no >= total_page:
                break
            page_no += 1

        return notices

    def filter_notices(self, notices: list[dict]) -> list[DisclosureItem]:
        """감시 대상 기업 + 키워드 매칭 공시만 추출."""
        matched: list[DisclosureItem] = []
        for n in notices:
            corp_name = n.get("corp_name", "")
            report_nm = n.get("report_nm", "")
            if corp_name not in self.companies:
                continue
            if not any(kw in report_nm for kw in self.keywords):
                continue
            matched.append(
                DisclosureItem(
                    corp_name=corp_name,
                    title=report_nm.strip(),
                    rcept_no=n.get("rcept_no", ""),
                    rcept_dt=n.get("rcept_dt", ""),
                    sector=get_company_sector(corp_name),
                )
            )
        return matched

    def run(self, target_date: datetime.date | None = None) -> list[DisclosureItem]:
        notices = self.fetch_notices(target_date)
        logger.info("Fetched %d total notices from DART.", len(notices))
        matched = self.filter_notices(notices)
        logger.info("Matched %d target disclosures.", len(matched))
        return matched
