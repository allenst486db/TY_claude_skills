# Claude Code 스킬 · 플러그인 · MCP 설치 가이드

작성일: 2026-07-25 · 대상 환경: Windows 11 / Claude Code 2.1.214 / Node v24.14.0

이번에 추가한 7개 항목의 **출처 · 설치 방법 · 사용법 · 주의사항**을 정리한 문서입니다.
새 머신에서 동일하게 재현하려면 [`scripts/install-claude-skills.ps1`](../scripts/install-claude-skills.ps1)
(또는 `.sh`)을 실행하면 되고, 기계가 읽는 명세는 [`claude-stack.json`](../claude-stack.json)에 있습니다.

---

## 0. 한눈에 보기

| # | 항목 | 형태 | 출처 | 상태 |
|---|------|------|------|------|
| 1 | deep-research | 스킬 | `199-biotechnologies/claude-deep-research-skill` | 설치 완료 |
| 2 | karpathy-guidelines | 플러그인 | `forrestchang/andrej-karpathy-skills` v1.0.0 | 설치 완료 |
| 3 | caveman | 플러그인 | `JuliusBrussee/caveman` | 설치 완료 (자동 활성화 OFF) |
| 4 | ui-ux-pro-max | 플러그인 | `nextlevelbuilder/ui-ux-pro-max-skill` v2.11.0 | 기존 설치 확인 |
| 5 | handoff | 플러그인 | `thepushkarp/handoff` v0.2.0 | 설치 완료 |
| 6 | Ruflo | MCP 서버 | npm `ruflo` v3.32.9 | 등록 완료 · 연결 확인 |
| 7 | NotebookLM | MCP 서버 | npm `notebooklm-mcp` v2.0.0 | 등록 완료 · **Google 인증 필요** |

> 설치 범위는 전부 **user(전역) 스코프**입니다. 이 저장소를 포함한 모든 프로젝트에서 바로 쓸 수 있습니다.
> **새 스킬/플러그인은 Claude Code를 재시작해야 로드됩니다.**

---

## 1. deep-research — 인용 추적 리서치 파이프라인

여러 소스를 교차 검증하고, 근거를 파일로 남기고, 인용이 붙은 리포트를 생성합니다.
단순 검색 1~2회로 끝나는 질문에는 쓰지 않습니다(스킬 자체가 그런 요청은 거절하도록 설계되어 있음).

### 설치
```bash
git clone --depth 1 https://github.com/199-biotechnologies/claude-deep-research-skill.git ~/.claude/skills/deep-research
```

### 사용
```
deep research on 2026년 국내 전기차 보조금 정책 변화
deep research in ultradeep mode: Postgres vs. ClickHouse 분석 워크로드 비교
```

4가지 모드가 있습니다.

| 모드 | 단계 | 대략 소요 | 용도 |
|---|---|---|---|
| quick | 3 | 2–5분 | 초기 탐색 |
| standard | 6 | 10–20분 | 일반 리서치 |
| deep | 8 | 30분+ | 의사결정용 리포트 |
| ultradeep | 8+ | 그 이상 | 정밀 비교·검증 |

리포트는 `~/Documents/[주제]_Research_[날짜]/` 에 Markdown / HTML / PDF로 저장됩니다.

### 의존성
- **필수**: Python 3.9+ (표준 라이브러리만 사용, `pip install` 불필요)
- **선택**: `weasyprint` (PDF 출력), `search-cli` (Brave/Serper/Exa/Jina/Firecrawl 검색 집계 — API 키 필요)

### 선택 설정 — 권한 프롬프트 줄이기
리서치 서브에이전트가 도구를 쓸 때마다 확인창이 뜨는 게 번거로우면
`~/.claude/settings.json` 에 아래를 **추가**합니다(기존 키는 유지).

```json
{
  "permissions": {
    "allow": ["WebSearch", "WebFetch", "Glob", "Grep", "Read"]
  }
}
```

> 이번 작업에서는 이 설정을 **적용하지 않았습니다.** `WebFetch` 자동 승인은 임의 URL 접근을
> 확인 없이 허용하는 것이라 판단이 필요한 항목이라서, 선택 사항으로 남겨둡니다.
> 없어도 deep-research는 정상 동작하며, 확인창이 몇 번 더 뜰 뿐입니다.

---

## 2. karpathy-guidelines — LLM 코딩 실수 줄이기

Andrej Karpathy가 지적한 LLM 코딩의 전형적 실패 패턴을 규칙으로 만든 스킬입니다.
코드를 쓰거나 리뷰·리팩터링할 때 자동으로 걸립니다.

### 설치
```bash
claude plugin marketplace add forrestchang/andrej-karpathy-skills
claude plugin install andrej-karpathy-skills@karpathy-skills
```

### 4대 원칙
1. **Think Before Coding** — 가정을 명시하고, 해석이 여러 개면 다 꺼내놓고, 모르면 멈추고 묻는다.
2. **Simplicity First** — 요청된 것만. 1회용 코드에 추상화 금지, 불가능한 예외의 에러 처리 금지.
3. **Surgical Changes** — 건드려야 할 것만. 옆 코드 "개선"·포맷 정리 금지.
4. **Goal-Driven Execution** — 검증 가능한 성공 기준을 먼저 정의한다.

> 트레이드오프: 속도보다 신중함 쪽으로 기울어 있습니다. 사소한 작업에서는 다소 답답할 수 있습니다.

---

## 3. caveman — 출력 토큰 압축

관사·군말·인사말·완충 표현을 걷어내고 문장 조각으로 답하게 만들어 **출력 토큰을 약 65% 절감**합니다.
코드·명령어·에러 메시지는 건드리지 않습니다.

### 설치
```bash
claude plugin marketplace add JuliusBrussee/caveman
claude plugin install caveman@caveman
```

### 이번 설정: 자동 활성화 OFF
기본 설치 상태에서는 SessionStart 훅이 **모든 세션 첫 메시지부터** caveman 말투를 강제합니다.
일상 작업 가독성을 해치므로 다음 파일을 만들어 껐습니다.

`%APPDATA%\caveman\config.json`
```json
{
  "defaultMode": "off"
}
```

필요할 때만 `/caveman` 으로 켜면 됩니다.

### 명령어
| 명령 | 설명 |
|---|---|
| `/caveman [lite\|full\|ultra\|wenyan]` | 압축 강도 전환 |
| `/caveman-commit` | 50자 이하 컨벤셔널 커밋 메시지 |
| `/caveman-review` | 한 줄짜리 PR 코멘트 |
| `/caveman-stats` | 세션/누적 토큰 절감량 |
| `/caveman-compress <file>` | CLAUDE.md 등 메모리 파일 압축(입력 토큰 ~46% 절감) |

### 모드 우선순위
`CAVEMAN_DEFAULT_MODE` 환경변수 → 저장소별 `.caveman/config.json` → 사용자 설정 → 기본값(`full`).
프로젝트 단위로 항상 켜고 싶으면 그 저장소에 `.caveman.json` 을 두면 됩니다.

---

## 4. ui-ux-pro-max — 이미 설치되어 있음

v2.11.0이 user 스코프로 설치·활성화된 상태였습니다. **재설치하지 않았습니다.**

제공 스킬: `ui-ux-pro-max`, `design`, `design-system`, `ui-styling`, `brand`, `banner-design`, `slides`

업데이트가 필요하면:
```bash
claude plugin update ui-ux-pro-max@ui-ux-pro-max-skill
```

> 이 저장소의 `CLAUDE.md` 는 Astryx 디자인 시스템 사용을 강제합니다.
> UI 작업 시 ui-ux-pro-max의 일반 조언보다 **CLAUDE.md 규칙(No `<div>`, 토큰 사용 등)이 우선**입니다.

---

## 5. handoff — 세션 간 인수인계

컨텍스트가 압축되거나 세션이 끊겨도 다음 세션이 이어서 작업할 수 있게 상태를 파일로 남깁니다.

### 설치
```bash
claude plugin marketplace add thepushkarp/handoff
claude plugin install handoff@handoff
```

### 명령어
| 명령 | 설명 |
|---|---|
| `/handoff:create` | 현재 작업 상태·결정·수정 파일·막힌 지점·다음 단계를 `docs/handoff/HANDOFF.md` 에 기록 |
| `/handoff:resume` | 기록을 읽어 컨텍스트 복원 |
| `/handoff:resume --auto` | 복원 후 곧바로 작업 재개 |

컨텍스트 압축 직전에 스냅샷을 남기고 압축 후 다시 주입하는 훅이 포함되어 있습니다.
`jq` 가 있으면 더 자세히 기록하지만, 없어도 동작합니다.

---

## 6. Ruflo — 멀티 에이전트 오케스트레이션 (MCP)

구 Claude Flow. 100여 개 전문 에이전트, 스웜 실행, 공유 메모리, 210여 개 MCP 도구를 제공합니다.

### 설치 (이번에 적용한 방식)
```bash
claude mcp add ruflo --scope user -- npx -y ruflo@latest mcp start
```

### ⚠️ `ruflo init` 을 실행하지 않은 이유
`npx ruflo init` 은 실행한 폴더에 `.claude/`, `.claude-flow/`, **`CLAUDE.md`** 를 생성합니다.
이 저장소에는 이미 Astryx 규칙이 담긴 `CLAUDE.md` 와 스킬 심볼릭 링크가 든 `.claude/` 가 있어
**덮어쓸 위험**이 있습니다. 그래서 MCP 서버 등록만 했습니다.

init 기능이 필요해지면 반드시 **빈 하위 폴더**에서 실행하세요.
```bash
mkdir ruflo-workspace && cd ruflo-workspace
npx ruflo@latest init wizard
```

### 검증
- npm 버전 3.32.9 확인
- MCP `initialize` 핸드셰이크 1.8초 내 정상 응답 (`serverInfo.name = "ruflo"`)
- `claude mcp list` → ✔ Connected

> 첫 등록 직후 health check가 한 번 실패할 수 있습니다. npx가 패키지를 처음 내려받느라 걸린 시간 때문이며,
> 캐시된 뒤 재실행하면 정상 연결됩니다.

---

## 7. NotebookLM 연결 (MCP) — 인증 1단계 남음

내 NotebookLM 노트북에 근거해서 **인용이 붙은** 답변을 받습니다. 소스 추가, 오디오(팟캐스트) 생성도 가능합니다.

### 설치 (완료)
```bash
claude mcp add notebooklm --scope user -- npx -y notebooklm-mcp@latest
```
`claude mcp list` → ✔ Connected 확인됨.

### 남은 수동 단계 — Google 로그인
현재 세션은 비대화형이라 OAuth를 진행할 수 없습니다. **대화형 `claude` 세션**에서 아래를 수행하세요.

1. Claude에게 NotebookLM `setup_auth` 도구 실행을 요청합니다.
2. Chrome 창이 열립니다. Google 계정으로 로그인합니다(제한 시간 10분).
3. 쿠키가 사용자별 Chrome 프로필에 저장되어 이후 재인증이 불필요합니다.

문제가 생기면 `re_auth`(초기화 후 재인증) 또는 `cleanup_data`(전체 초기화)를 사용합니다.

### 주요 도구
- **질의**: `ask_question` (인용 추출 옵션)
- **소스**: `add_source` (URL/텍스트), `generate_audio`, `download_audio`
- **라이브러리**: `add_notebook`, `list_notebooks`, `search_notebooks`
- **시스템**: 헬스 체크, 인증 관리

### 요구사항
Node 18+, Chrome(안정 채널 권장 / 번들 Chromium 대체 가능).
Windows에서 WSL을 쓴다면 **WSL2 + WSLg 필요** (WSL1은 Chromium 실행 불가).
여러 계정은 `--account` 플래그로 분리합니다.

---

## 8. 변경된 파일 (전부 "추가" 방식)

| 파일 | 변경 |
|---|---|
| `~/.claude/settings.json` | `enabledPlugins` 에 3개, `extraKnownMarketplaces` 에 3개 **추가**. 기존 항목·테마 그대로 유지 |
| `~/.claude.json` | MCP 서버 `ruflo`, `notebooklm` 추가 |
| `~/.claude/skills/deep-research/` | 신규 clone |
| `~/.claude/plugins/` | 마켓플레이스 3개 + 플러그인 3개 캐시 |
| `%APPDATA%\caveman\config.json` | 신규 생성 (`defaultMode: off`) |
| 이 저장소 | `claude-stack.json`, `scripts/`, `docs/claude-skills-setup-guide.md`, `.gitignore` 신규 |

**건드리지 않은 것**: `CLAUDE.md`(전역/프로젝트 양쪽), `.claude/CLAUDE.md`, `skills-lock.json`,
`.agents/skills/` 하위 기존 스킬, 기존 심볼릭 링크.

> `skills-lock.json` 은 스킬 CLI가 관리하는 락파일이라 손대지 않았습니다.
> 이번에 추가한 스택은 별도 파일 `claude-stack.json` 에 기록했습니다.

---

## 9. 새 머신에서 동일하게 재현하기

```bash
git clone <이 저장소> && cd <저장소>
pwsh -File scripts/install-claude-skills.ps1     # Windows
bash scripts/install-claude-skills.sh            # macOS / Linux / Git Bash
```

스크립트는 멱등이라 여러 번 돌려도 안전하고, 이미 있는 항목은 건너뜁니다.
끝나면 NotebookLM 인증(7절)만 수동으로 하면 됩니다.

---

## 10. 제거 방법

```bash
# 플러그인
claude plugin uninstall caveman@caveman
claude plugin uninstall handoff@handoff
claude plugin uninstall andrej-karpathy-skills@karpathy-skills

# 마켓플레이스 등록 해제
claude plugin marketplace remove caveman

# MCP 서버
claude mcp remove ruflo --scope user
claude mcp remove notebooklm --scope user
```

deep-research 스킬은 `~/.claude/skills/deep-research` 폴더를 지우면 됩니다.

---

## 참고 링크

- [199-biotechnologies/claude-deep-research-skill](https://github.com/199-biotechnologies/claude-deep-research-skill)
- [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)
- [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)
- [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- [thepushkarp/handoff](https://github.com/thepushkarp/handoff)
- [ruvnet/ruflo](https://github.com/ruvnet/ruflo)
- [PleasePrompto/notebooklm-mcp](https://github.com/PleasePrompto/notebooklm-mcp)
