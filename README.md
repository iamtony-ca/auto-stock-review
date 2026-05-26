# auto-stock-review

대한민국 반도체 / AI 인프라 / Physical AI(로보틱스) 밸류체인 상장사들의 **DART 공시를 매일 자동으로 감시**하고, Gemini로 핵심을 요약해 **Slack으로 알림**을 보내는 서버리스 파이프라인입니다.

GitHub Actions 위에서 동작하므로 별도의 서버나 GPU가 필요 없습니다.

## 구조

```
[DART Open API] ──► [DartWatcher] ──► [GeminiProcessor] ──► [Slack / Console]
                       │                    │                    │
                  config/watch_list      core/llm.py         core/notifiers.py
```

- `config/watch_list.py` — 감시 대상 종목과 키워드 (수정 포인트)
- `core/interfaces.py` — `LLMProcessor`, `Notifier` 추상 인터페이스
- `core/dart_watcher.py` — DART API 조회 + 기업/키워드 필터
- `core/llm.py` — Gemini 구현체 (Claude/OpenAI 교체 가능)
- `core/notifiers.py` — Console / Slack / Multi 채널
- `main.py` — 의존성 조립 + 실행 엔트리포인트
- `.github/workflows/daily-watcher.yml` — 평일 16:30 KST 자동 실행

## 셋업

### 1. API 키 발급

| 서비스 | URL | 비용 |
| --- | --- | --- |
| DART Open API | https://opendart.fss.or.kr | 무료 |
| Google Gemini API | https://aistudio.google.com/app/apikey | 무료 티어 |
| Slack Incoming Webhook | https://api.slack.com/messaging/webhooks | 무료 |

### 2. GitHub Secrets 등록

저장소 `Settings → Secrets and variables → Actions` 에 다음 3개를 등록:

- `DART_API_KEY`
- `GEMINI_API_KEY`
- `SLACK_WEBHOOK_URL`

### 3. 로컬 실행

```bash
pip install -r requirements.txt
export DART_API_KEY=...
export GEMINI_API_KEY=...
export SLACK_WEBHOOK_URL=...   # 생략 시 콘솔에만 출력
python main.py
```

옵션:
- `--date YYYY-MM-DD` — 특정 날짜 조회 (백테스트)
- `--dry-run` — Slack 전송 없이 콘솔만
- `--quiet-when-empty` — 공시 0건일 때 알림 생략
- `--verbose` — 디버그 로그

## 종목/키워드 추가

`config/watch_list.py` 의 `WATCH_COMPANIES` 딕셔너리에 추가하면 끝입니다.
키워드는 `TARGET_KEYWORDS` 리스트에 추가.

## LLM/알림 채널 교체

- 다른 LLM: `core/llm.py` 에 `LLMProcessor` 를 상속받는 클래스를 추가하고 `main.build_llm()` 에서 교체
- 다른 알림 채널: `core/notifiers.py` 에 `Notifier` 상속 클래스를 추가하고 `main.build_notifier()` 에 끼워넣기

## 자동 실행

`.github/workflows/daily-watcher.yml` 에 따라 **평일 한국 시간 16:30 (장 마감 직후)** 에 자동 실행됩니다.
`workflow_dispatch` 로 수동 실행도 가능하며, 임의 날짜 입력도 지원합니다.
