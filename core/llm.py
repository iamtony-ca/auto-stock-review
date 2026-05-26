"""
LLM 백엔드 구현체.

기본은 Google Gemini (무료 티어 활용).
추후 Claude / OpenAI 등 추가 시 LLMProcessor 상속만 받으면 된다.
"""

import logging
import textwrap

import google.generativeai as genai

from core.interfaces import DisclosureItem, LLMProcessor

logger = logging.getLogger(__name__)


class GeminiProcessor(LLMProcessor):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        if not api_key:
            raise ValueError("Gemini API key is required")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

    def summarize_disclosure(self, item: DisclosureItem) -> str:
        prompt = textwrap.dedent(
            f"""
            당신은 대한민국 반도체 및 로보틱스 산업 전문 기업분석 애널리스트입니다.
            아래 신규 공시 정보를 바탕으로 투자자가 주목해야 할 핵심 포인트를
            아래 출력 양식에 정확히 맞춰 한국어로 작성하세요.

            [공시 정보]
            - 기업명: {item.corp_name}
            - 섹터: {item.sector or '미분류'}
            - 공시 종류: {item.title}
            - 접수일자: {item.rcept_dt}

            [작성 지침]
            - 추측을 사실처럼 단정하지 말 것.
            - 제목에서 유추 가능한 산업적 의미를 1문장 보강할 것.
            - 이모지는 양식에 명시된 것만 사용할 것.

            [출력 양식]
            :rotating_light: *[{item.corp_name}] {item.title}*
            • *공시 요약:* (제목 기반 1문장 요약)
            • *투자자 관점 해석:* (해당 이벤트의 반도체/AI/로봇 생태계 내 의미 1~2문장)
            • *원본 보기:* <{item.dart_url}|DART 공시 원문 바로가기>
            """
        ).strip()

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.exception("Gemini API call failed for %s", item.corp_name)
            return self._fallback_message(item, error=str(e))

    @staticmethod
    def _fallback_message(item: DisclosureItem, error: str = "") -> str:
        """LLM 호출 실패 시에도 알림은 가도록 fallback 메시지 생성."""
        err_line = f"\n• _AI 요약 실패: {error}_" if error else ""
        return (
            f":rotating_light: *[{item.corp_name}] {item.title}*\n"
            f"• *섹터:* {item.sector or '미분류'}\n"
            f"• *접수일자:* {item.rcept_dt}\n"
            f"• *원본 보기:* <{item.dart_url}|DART 공시 원문 바로가기>"
            f"{err_line}"
        )
