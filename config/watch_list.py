"""
감시 대상 종목 및 키워드 설정.

종목을 추가/제거하려면 이 파일만 수정하면 됩니다.
카테고리별로 분류되어 있어 섹터별 필터링도 가능합니다.
"""

WATCH_COMPANIES = {
    "AI_SEMI_IDM": [
        "삼성전자",
        "SK하이닉스",
    ],
    "AI_SEMI_IP": [
        "오픈엣지테크놀로지",
        "칩스앤미디어",
        "퀄리타스반도체",
    ],
    "AI_SEMI_DESIGN_HOUSE": [
        "가온칩스",
        "에이디테크놀로지",
        "코아시아",
    ],
    "AI_SEMI_BACKEND_EQUIPMENT": [
        "한미반도체",
        "에이치피에스피",
        "에스티아이",
        "피에스케이홀딩스",
        "넥스틴",
        "고영테크놀러지",
    ],
    "AI_SEMI_OSAT": [
        "하나마이크론",
        "두산테스나",
        "네패스",
    ],
    "AI_INFRA_COOLING": [
        "한온시스템",
        "LG전자",
    ],
    "AI_INFRA_POWER": [
        "HD현대일렉트릭",
        "LS일렉트릭",
        "지엔씨에너지",
    ],
    "AI_INFRA_SOFTWARE": [
        "모아데이타",
        "크라우드웍스",
        "코난테크놀로지",
    ],
    "PHYSICAL_AI_REDUCER": [
        "에스피지",
        "에스비비테크",
        "해성티피씨",
    ],
    "PHYSICAL_AI_ACTUATOR": [
        "로보티즈",
        "하이젠알앤엠",
    ],
    "PHYSICAL_AI_MOTION_SENSOR": [
        "알에스오토메이션",
        "에스오에스랩",
        "씨메스",
    ],
    "PHYSICAL_AI_MODULE": [
        "싸이맥스",
        "라온테크",
        "로보스타",
        "아진엑스텍",
    ],
    "PHYSICAL_AI_SYSTEM": [
        "두산로보틱스",
        "레인보우로보틱스",
        "티라유텍",
        "에스엠코어",
    ],
}


def get_all_companies() -> list[str]:
    """카테고리에 등록된 모든 기업명을 단일 리스트로 반환."""
    return sorted({c for companies in WATCH_COMPANIES.values() for c in companies})


def get_company_sector(company_name: str) -> str | None:
    """기업명에 해당하는 카테고리 키를 반환. 없으면 None."""
    for sector, companies in WATCH_COMPANIES.items():
        if company_name in companies:
            return sector
    return None


TARGET_KEYWORDS = [
    "공급계약",
    "단일판매",
    "지분취득",
    "타법인 주식",
    "투자판단",
    "특허권",
    "주요사항보고서",
    "유상증자",
    "무상증자",
    "전환사채",
    "신주인수권",
    "합병",
    "분할",
    "자기주식",
]
