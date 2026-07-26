# install-claude-skills.ps1
#
# claude-stack.json 에 정의된 Claude Code 스택을 새 머신에서 그대로 재현합니다.
# 모든 단계는 멱등(idempotent)하며, 이미 설치된 항목은 건너뜁니다.
# 기존 settings.json / CLAUDE.md 를 덮어쓰지 않습니다.
#
# 사용법:  pwsh -File scripts/install-claude-skills.ps1

$ErrorActionPreference = 'Stop'

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Skip($msg) { Write-Host "    (건너뜀) $msg" -ForegroundColor DarkGray }

# ---------------------------------------------------------------- 사전 점검
Write-Step '사전 점검'
foreach ($cmd in @('claude', 'git', 'node', 'npx')) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        throw "$cmd 를 찾을 수 없습니다. 먼저 설치하세요."
    }
    Write-Host "    OK: $cmd"
}

$claudeDir = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME '.claude' }

# ------------------------------------------------------------ 1. 마켓플레이스
Write-Step '플러그인 마켓플레이스 등록'
$marketplaces = @(
    @{ name = 'claude-plugins-official'; repo = 'anthropics/claude-plugins-official' },
    @{ name = 'thedotmack';           repo = 'thedotmack/claude-mem' },
    @{ name = 'karpathy-skills';      repo = 'forrestchang/andrej-karpathy-skills' },
    @{ name = 'caveman';              repo = 'JuliusBrussee/caveman' },
    @{ name = 'handoff';              repo = 'thepushkarp/handoff' },
    @{ name = 'ui-ux-pro-max-skill';  repo = 'nextlevelbuilder/ui-ux-pro-max-skill' },
    @{ name = 'claude-video';         repo = 'bradautomates/claude-video' },
    @{ name = 'ponytail';             repo = 'DietrichGebert/ponytail' },
    @{ name = 'impeccable';           repo = 'pbakaus/impeccable' }
)
foreach ($m in $marketplaces) {
    Write-Host "  - $($m.repo)"
    claude plugin marketplace add $m.repo 2>&1 | Select-Object -Last 1
}

# ---------------------------------------------------------------- 2. 플러그인
Write-Step '플러그인 설치'
$plugins = @(
    'superpowers@claude-plugins-official',
    'claude-mem@thedotmack',
    'andrej-karpathy-skills@karpathy-skills',
    'caveman@caveman',
    'handoff@handoff',
    'ui-ux-pro-max@ui-ux-pro-max-skill',
    'watch@claude-video',
    'ponytail@ponytail',
    'impeccable@impeccable'
)
foreach ($p in $plugins) {
    Write-Host "  - $p"
    claude plugin install $p 2>&1 | Select-Object -Last 1
}

# ------------------------------------------------------- 3. caveman 기본값 off
Write-Step 'caveman 자동 활성화 끄기 (필요할 때 /caveman 으로 진입)'
$cavemanDir = Join-Path $env:APPDATA 'caveman'
$cavemanCfg = Join-Path $cavemanDir 'config.json'
if (Test-Path $cavemanCfg) {
    Write-Skip "$cavemanCfg 이미 존재 — 수동 확인 필요 (defaultMode: off)"
} else {
    New-Item -ItemType Directory -Force -Path $cavemanDir | Out-Null
    '{
  "defaultMode": "off"
}' | Set-Content -Path $cavemanCfg -Encoding UTF8
    Write-Host "    작성됨: $cavemanCfg"
}

# ------------------------------------------------------- 4. deep-research 스킬
Write-Step 'deep-research 스킬 설치'
$drPath = Join-Path $claudeDir 'skills\deep-research'
if (Test-Path $drPath) {
    Write-Skip "$drPath 이미 존재"
} else {
    New-Item -ItemType Directory -Force -Path (Split-Path $drPath) | Out-Null
    git clone --depth 1 https://github.com/199-biotechnologies/claude-deep-research-skill.git $drPath
}

# --------------------------------------------- 5. mosikdo-guide 스킬 (가이드 문서 스타일)
Write-Step 'mosikdo-guide 스킬 설치 (macOS 스타일 HTML 가이드 + SVG 모식도)'
$mgPath = Join-Path $claudeDir 'skills\mosikdo-guide'
if (Test-Path $mgPath) {
    Write-Skip "$mgPath 이미 존재"
} else {
    $tmpTy = Join-Path ([System.IO.Path]::GetTempPath()) ("ty_" + [guid]::NewGuid().ToString('N').Substring(0,8))
    git clone --depth 1 https://github.com/allenst486db/TY_claude_skills.git $tmpTy
    New-Item -ItemType Directory -Force -Path (Split-Path $mgPath) | Out-Null
    Copy-Item (Join-Path $tmpTy 'mosikdo-guide') $mgPath -Recurse
    Remove-Item $tmpTy -Recurse -Force
    Write-Host "    설치됨: $mgPath"
}

# ------------------------------------------- 6. pip 기반 스킬 (graphify, notebooklm-py)
Write-Step 'pip 기반 스킬 설치 (graphify · notebooklm-py)'
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host '    python 을 찾을 수 없어 graphify/notebooklm-py 를 건너뜁니다.' -ForegroundColor Yellow
} else {
    # pip --user 설치 스크립트 경로를 이번 세션 PATH 에 임시로 추가
    $userScripts = python -c "import sysconfig;print(sysconfig.get_path('scripts',scheme='nt_user'))" 2>$null
    if ($userScripts -and (Test-Path $userScripts) -and ($env:Path -notlike "*$userScripts*")) {
        $env:Path = "$env:Path;$userScripts"
    }

    # graphify — PyPI 이름은 graphifyy, CLI 는 graphify
    python -m pip install --disable-pip-version-check --quiet graphifyy
    graphify install    # ~/.claude/skills/graphify + CLAUDE.md 트리거 한 줄 append

    # notebooklm-py — CLI + Playwright 브라우저 자동화
    python -m pip install --disable-pip-version-check --quiet "notebooklm-py[browser]"
    notebooklm skill install
    playwright install chromium

    # claude-video(/watch) 의 필수 의존성
    python -m pip install --disable-pip-version-check --quiet yt-dlp

    Write-Host "    사용자 스크립트 경로: $userScripts" -ForegroundColor DarkGray
    if ($userScripts -and (([Environment]::GetEnvironmentVariable('Path','User') -split ';') -notcontains $userScripts)) {
        Write-Host '    ↑ 이 경로를 사용자 PATH 에 추가해야 graphify/notebooklm/yt-dlp 명령이 잡힙니다.' -ForegroundColor Yellow
    }
}

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host '    ffmpeg 미설치 — /watch 가 동작하지 않습니다. 수동 설치: winget install Gyan.FFmpeg' -ForegroundColor Yellow
}

# ---------------------------------------------------------------- 7. MCP 서버
Write-Step 'MCP 서버 등록 (user 스코프)'
$existing = (claude mcp list 2>&1 | Out-String)

if ($existing -match '(?m)^\s*ruflo:') {
    Write-Skip 'ruflo 이미 등록됨'
} else {
    claude mcp add ruflo --scope user -- npx -y ruflo@latest mcp start
}

if ($existing -match '(?m)^\s*notebooklm:') {
    Write-Skip 'notebooklm 이미 등록됨'
} else {
    claude mcp add notebooklm --scope user -- npx -y notebooklm-mcp@latest
}

# ------------------------------------------------------------------- 마무리
Write-Step '완료'
Write-Host @'
남은 수동 단계:
  1. NotebookLM 인증 — (a) MCP: 대화형 claude 세션에서 setup_auth 도구 실행,
     (b) CLI: notebooklm login  → 둘 다 브라우저 창에서 Google 로그인이 필요합니다.
     확인: notebooklm auth check --test
  1-b. ffmpeg 설치 (claude-video /watch 필수):  winget install Gyan.FFmpeg
  1-c. 프로젝트별 1회:  /impeccable init  (PRODUCT.md / DESIGN.md 생성)
  2. (선택) deep-research 서브에이전트의 권한 프롬프트를 줄이려면
     ~/.claude/settings.json 의 permissions.allow 에
     "WebSearch", "WebFetch", "Glob", "Grep", "Read" 를 추가하세요.
     WebFetch 자동 승인은 임의 URL 접근을 무확인 허용하므로 판단 후 적용하세요.
  3. claude 를 재시작해야 새 스킬/플러그인이 로드됩니다.
'@ -ForegroundColor Yellow
