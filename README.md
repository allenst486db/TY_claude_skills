# Claude Code 스킬 · 유용 자료

내 Claude Code 스택을 **재현 가능한 형태로** 기록하는 저장소입니다.
플러그인 9 · 스킬 4 · MCP 서버 2 = **15개 항목**.

| 무엇 | 어디 |
|---|---|
| 사람이 읽는 통합 가이드 | **[`docs/claude-stack-guide.html`](docs/claude-stack-guide.html)** |
| 기계가 읽는 명세 | [`claude-stack.json`](claude-stack.json) |
| 새 머신 재현 스크립트 | [`scripts/install-claude-skills.ps1`](scripts/install-claude-skills.ps1) · [`.sh`](scripts/install-claude-skills.sh) |

> 통합 가이드는 `mosikdo-guide` 스킬(macOS 스타일 HTML + 인라인 SVG 모식도)로 작성했습니다.
> 모식도 9개로 설치 구조 · `/watch` 파이프라인 · graphify 그래프 · ponytail 결정 래더 ·
> caveman 분기 · ruflo init 위험을 그림으로 정리해 뒀습니다. GitHub 에서는 raw 로 보이니
> 파일을 내려받아 브라우저로 열거나 GitHub Pages 로 보세요.

---

## 빠른 시작

```bash
git clone <이 저장소> && cd <저장소>
```

Windows:

```bash
pwsh -File scripts/install-claude-skills.ps1
```

macOS / Linux / Git Bash:

```bash
bash scripts/install-claude-skills.sh
```

스크립트는 **멱등**이라 여러 번 돌려도 안전하고, 이미 설치된 항목은 건너뜁니다.
`settings.json` · `CLAUDE.md` 는 덮어쓰지 않고 **추가만** 합니다.

---

## 스택

설치 시점이 아니라 **어떤 결핍을 메우는가**로 묶었습니다.

### ① 입력을 읽힌다 — Claude 가 원래 못 보는 재료

| 항목 | 형태 | 출처 | 상태 |
|---|---|---|---|
| `/watch` | 플러그인 0.2.0 | [bradautomates/claude-video](https://github.com/bradautomates/claude-video) | ⚠️ ffmpeg 필요 |
| notebooklm (CLI) | 스킬 0.7.3 | [teng-lin/notebooklm-py](https://github.com/teng-lin/notebooklm-py) | ⚠️ 로그인 필요 |
| notebooklm (MCP) | MCP 2.0.0 | [PleasePrompto/notebooklm-mcp](https://github.com/PleasePrompto/notebooklm-mcp) | ⚠️ 인증 · 스코프 중복 |
| deep-research | 스킬 | [199-biotechnologies/claude-deep-research-skill](https://github.com/199-biotechnologies/claude-deep-research-skill) | ✅ |

### ② 코드베이스를 본다

| 항목 | 형태 | 출처 | 상태 |
|---|---|---|---|
| `/graphify` | 스킬 0.9.26 | [safishamsi/graphify](https://github.com/safishamsi/graphify) | ✅ |

폴더를 tree-sitter AST 기반 지식 그래프로 만듭니다. 벡터 스토어 없음, 전부 로컬, 엣지마다 근거가 붙습니다.

### ③ 만들 때 붙는다 — 품질 게이트

| 항목 | 형태 | 출처 | 상태 |
|---|---|---|---|
| `/impeccable` | 플러그인 4.0.2 | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | ⚠️ `init` 필요 |
| `/ponytail` | 플러그인 4.8.4 | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | ✅ 기본 `full` |
| karpathy-guidelines | 플러그인 1.0.0 | [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) | ✅ |

impeccable 은 **디자인**을, ponytail 은 **코드량**을 줄입니다. 겹치지 않습니다.

### ④ 문서·UI 를 만든다

| 항목 | 형태 | 출처 | 상태 |
|---|---|---|---|
| mosikdo-guide | 스킬 | [allenst486db/TY_claude_skills](https://github.com/allenst486db/TY_claude_skills) | ✅ |
| ui-ux-pro-max | 플러그인 2.11.0 | [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | ✅ |

UI 작업에서는 이 저장소 `CLAUDE.md` 의 **Astryx 규칙이 우선**입니다.

### ⑤ 세션·토큰을 관리한다

| 항목 | 형태 | 출처 | 상태 |
|---|---|---|---|
| `/caveman` | 플러그인 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | ✅ 자동 활성화 **OFF** |
| `/handoff` | 플러그인 0.2.0 | [thepushkarp/handoff](https://github.com/thepushkarp/handoff) | ✅ |
| claude-mem | 플러그인 13.11.0 | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | ✅ |

caveman 은 **출력 토큰**을, ponytail 은 **쓰는 코드량**을 줄입니다 — 같이 켜도 됩니다.

### ⑥ 실행을 확장한다

| 항목 | 형태 | 출처 | 상태 |
|---|---|---|---|
| superpowers | 플러그인 6.2.0 | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | ✅ |
| ruflo | MCP 3.32.9 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | ✅ Connected |

> ⛔ **`ruflo init` 은 이 저장소에서 실행하지 마세요.** 실행한 폴더에 `.claude/` · `.claude-flow/` ·
> `CLAUDE.md` 를 만들기 때문에 기존 Astryx 규칙과 스킬 링크가 날아갑니다. MCP 등록만 했습니다.
> init 이 필요하면 **빈 하위 폴더**에서 돌리세요.

---

## 남은 수동 단계

라이선스 동의 · 계정 로그인 · 프로젝트별 초기화라서 스크립트가 대신 못 합니다.

```bash
winget install Gyan.FFmpeg
```

```bash
notebooklm login
```

```bash
claude mcp remove notebooklm -s local
```

- `/impeccable init` — 프론트엔드 작업이 있는 저장소에서 1회
- **Claude Code 재시작** — 새 플러그인 커맨드(`/watch` · `/ponytail` · `/impeccable`)는 재시작 후 등록됩니다
- (선택) `GROQ_API_KEY` 또는 `OPENAI_API_KEY` — 자막 없는 영상 전사용

### 알려진 문제 3

1. **ffmpeg 미설치** → `/watch` 미동작. `yt-dlp` 는 설치됨.
2. **NotebookLM 인증 미완료** → `notebooklm auth check` 실패 상태. CLI 와 MCP 는 인증이 **별도**입니다.
3. **notebooklm MCP 스코프 중복** → user / local 두 스코프에 엔드포인트가 달라서 한쪽 인증이 다른 쪽에 적용되지 않습니다. 로그인 **전에** local 을 제거하세요.

---

## Windows PATH 주의

pip 는 실행 파일을 `%APPDATA%\Python\Python3xx\Scripts` 에 넣는데 이 경로가 PATH 에 없을 수 있습니다.
없으면 `graphify` · `notebooklm` · `yt-dlp` 명령이 잡히지 않습니다.

```bash
python -c "import sysconfig;print(sysconfig.get_path('scripts',scheme='nt_user'))"
```

출력된 경로를 사용자 PATH 에 **추가**하고 터미널을 새로 여세요.

---

## 저장소 구조

```
README.md                                이 파일 — 스택 index
claude-stack.json                        기계용 명세 (설치 스크립트가 재현하는 목록)
scripts/install-claude-skills.ps1 · .sh  멱등 재현 스크립트
docs/claude-stack-guide.html             통합 가이드 (모식도 9개)
docs/astryx-migration-guide.html         Tailwind/shadcn → Astryx 마이그레이션
참고 자료 파일/                           외부에서 저장한 웹페이지 원본
skills-lock.json                         스킬 CLI 전용 락파일 — 손대지 않음
```

`skills-lock.json` 은 스킬 CLI 가 관리하는 파일이라 `claude-stack.json` 과 **별개**이고
서로 덮어쓰지 않습니다.

---

## 검증 환경

Windows 11 10.0.26200 · Claude Code 2.1.214 · Node v24.14.0 · Python 3.14.3 · 2026-07-25

버전과 플래그는 각 저장소 README 기준이라 업스트림 변경 시 달라질 수 있습니다.
특히 `notebooklm-py` 는 Google 의 문서화되지 않은 API 를 쓰므로 예고 없이 깨질 수 있습니다.
