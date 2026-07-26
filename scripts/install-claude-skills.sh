#!/usr/bin/env bash
# install-claude-skills.sh
#
# claude-stack.json 에 정의된 Claude Code 스택을 새 머신에서 그대로 재현합니다.
# 모든 단계는 멱등(idempotent)하며, 이미 설치된 항목은 건너뜁니다.
# 기존 settings.json / CLAUDE.md 를 덮어쓰지 않습니다.
#
# 사용법:  bash scripts/install-claude-skills.sh

set -euo pipefail

step() { printf '\n==> %s\n' "$1"; }
skip() { printf '    (건너뜀) %s\n' "$1"; }

# ---------------------------------------------------------------- 사전 점검
step "사전 점검"
for cmd in claude git node npx; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "$cmd 를 찾을 수 없습니다. 먼저 설치하세요." >&2; exit 1; }
  echo "    OK: $cmd"
done

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"

# ------------------------------------------------------------ 1. 마켓플레이스
step "플러그인 마켓플레이스 등록"
for repo in \
  anthropics/claude-plugins-official \
  thedotmack/claude-mem \
  forrestchang/andrej-karpathy-skills \
  JuliusBrussee/caveman \
  thepushkarp/handoff \
  nextlevelbuilder/ui-ux-pro-max-skill \
  bradautomates/claude-video \
  DietrichGebert/ponytail \
  pbakaus/impeccable
do
  echo "  - $repo"
  claude plugin marketplace add "$repo" 2>&1 | tail -1
done

# ---------------------------------------------------------------- 2. 플러그인
step "플러그인 설치"
for p in \
  superpowers@claude-plugins-official \
  claude-mem@thedotmack \
  andrej-karpathy-skills@karpathy-skills \
  caveman@caveman \
  handoff@handoff \
  ui-ux-pro-max@ui-ux-pro-max-skill \
  watch@claude-video \
  ponytail@ponytail \
  impeccable@impeccable
do
  echo "  - $p"
  claude plugin install "$p" 2>&1 | tail -1
done

# ------------------------------------------------------- 3. caveman 기본값 off
step "caveman 자동 활성화 끄기 (필요할 때 /caveman 으로 진입)"
if [ -n "${XDG_CONFIG_HOME:-}" ]; then
  CAVEMAN_DIR="$XDG_CONFIG_HOME/caveman"
elif [ -n "${APPDATA:-}" ]; then
  CAVEMAN_DIR="$APPDATA/caveman"
else
  CAVEMAN_DIR="$HOME/.config/caveman"
fi
if [ -f "$CAVEMAN_DIR/config.json" ]; then
  skip "$CAVEMAN_DIR/config.json 이미 존재 — 수동 확인 필요 (defaultMode: off)"
else
  mkdir -p "$CAVEMAN_DIR"
  printf '{\n  "defaultMode": "off"\n}\n' > "$CAVEMAN_DIR/config.json"
  echo "    작성됨: $CAVEMAN_DIR/config.json"
fi

# ------------------------------------------------------- 4. deep-research 스킬
step "deep-research 스킬 설치"
if [ -d "$CLAUDE_DIR/skills/deep-research" ]; then
  skip "$CLAUDE_DIR/skills/deep-research 이미 존재"
else
  mkdir -p "$CLAUDE_DIR/skills"
  git clone --depth 1 https://github.com/199-biotechnologies/claude-deep-research-skill.git \
    "$CLAUDE_DIR/skills/deep-research"
fi

# --------------------------------------------- 5. mosikdo-guide 스킬 (가이드 문서 스타일)
step "mosikdo-guide 스킬 설치 (macOS 스타일 HTML 가이드 + SVG 모식도)"
if [ -d "$CLAUDE_DIR/skills/mosikdo-guide" ]; then
  skip "$CLAUDE_DIR/skills/mosikdo-guide 이미 존재"
else
  TMP_TY="$(mktemp -d)"
  git clone --depth 1 https://github.com/allenst486db/TY_claude_skills.git "$TMP_TY/repo"
  mkdir -p "$CLAUDE_DIR/skills"
  cp -r "$TMP_TY/repo/mosikdo-guide" "$CLAUDE_DIR/skills/mosikdo-guide"
  rm -rf "$TMP_TY"
  echo "    설치됨: $CLAUDE_DIR/skills/mosikdo-guide"
fi

# ------------------------------------------- 6. pip 기반 스킬 (graphify, notebooklm-py)
step "pip 기반 스킬 설치 (graphify · notebooklm-py)"
PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ]; then
  echo "    python 을 찾을 수 없어 graphify/notebooklm-py 를 건너뜁니다."
else
  # pip --user 설치 스크립트 경로를 이번 세션 PATH 에 임시로 추가
  USER_SCRIPTS="$("$PY" -c 'import sysconfig,os;print(sysconfig.get_path("scripts",scheme=("nt_user" if os.name=="nt" else "posix_user")))' 2>/dev/null || true)"
  case ":$PATH:" in
    *":$USER_SCRIPTS:"*) ;;
    *) [ -n "$USER_SCRIPTS" ] && PATH="$PATH:$USER_SCRIPTS" ;;
  esac

  # graphify — PyPI 이름은 graphifyy, CLI 는 graphify
  "$PY" -m pip install --disable-pip-version-check --quiet graphifyy
  graphify install    # ~/.claude/skills/graphify + CLAUDE.md 트리거 한 줄 append

  # notebooklm-py — CLI + Playwright 브라우저 자동화
  "$PY" -m pip install --disable-pip-version-check --quiet "notebooklm-py[browser]"
  notebooklm skill install
  playwright install chromium

  # claude-video(/watch) 의 필수 의존성
  "$PY" -m pip install --disable-pip-version-check --quiet yt-dlp

  echo "    사용자 스크립트 경로: ${USER_SCRIPTS:-?} (셸 rc 의 PATH 에 추가하세요)"
fi

command -v ffmpeg >/dev/null 2>&1 || \
  echo "    ffmpeg 미설치 — /watch 가 동작하지 않습니다. macOS: brew install ffmpeg / Windows: winget install Gyan.FFmpeg"

# ---------------------------------------------------------------- 7. MCP 서버
step "MCP 서버 등록 (user 스코프)"
EXISTING="$(claude mcp list 2>&1 || true)"

if printf '%s' "$EXISTING" | grep -qE '^\s*ruflo:'; then
  skip "ruflo 이미 등록됨"
else
  claude mcp add ruflo --scope user -- npx -y ruflo@latest mcp start
fi

if printf '%s' "$EXISTING" | grep -qE '^\s*notebooklm:'; then
  skip "notebooklm 이미 등록됨"
else
  claude mcp add notebooklm --scope user -- npx -y notebooklm-mcp@latest
fi

# ------------------------------------------------------------------- 마무리
step "완료"
cat <<'EOF'
남은 수동 단계:
  1. NotebookLM 인증 — (a) MCP: 대화형 claude 세션에서 setup_auth 도구 실행,
     (b) CLI: notebooklm login  → 둘 다 브라우저 창에서 Google 로그인이 필요합니다.
     확인: notebooklm auth check --test
  1-b. ffmpeg 설치 (claude-video /watch 필수):
     macOS: brew install ffmpeg / Windows: winget install Gyan.FFmpeg
  1-c. 프로젝트별 1회:  /impeccable init  (PRODUCT.md / DESIGN.md 생성)
  2. (선택) deep-research 서브에이전트의 권한 프롬프트를 줄이려면
     ~/.claude/settings.json 의 permissions.allow 에
     "WebSearch", "WebFetch", "Glob", "Grep", "Read" 를 추가하세요.
     WebFetch 자동 승인은 임의 URL 접근을 무확인 허용하므로 판단 후 적용하세요.
  3. claude 를 재시작해야 새 스킬/플러그인이 로드됩니다.
EOF
