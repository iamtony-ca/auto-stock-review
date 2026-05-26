"""
추상 인터페이스 정의.

LLM 엔진과 Notifier(알림 채널)를 플러그인처럼 교체할 수 있도록
ABC(Abstract Base Class) 기반 인터페이스를 분리한다.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DisclosureItem:
    """DART 공시 1건을 표현하는 데이터 객체."""

    corp_name: str
    title: str
    rcept_no: str
    rcept_dt: str
    sector: str | None = None

    @property
    def dart_url(self) -> str:
        return f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={self.rcept_no}"


class LLMProcessor(ABC):
    """LLM 백엔드 교체용 인터페이스 (Gemini / Claude / OpenAI 등)."""

    @abstractmethod
    def summarize_disclosure(self, item: DisclosureItem) -> str:
        """공시 1건을 사람이 읽기 좋은 요약으로 변환."""


class Notifier(ABC):
    """알림 채널 교체용 인터페이스 (Slack / Telegram / Email 등)."""

    @abstractmethod
    def send(self, message: str) -> bool:
        """메시지를 채널에 전송. 성공 여부 반환."""

    @property
    def name(self) -> str:
        return self.__class__.__name__
