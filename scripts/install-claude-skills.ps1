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
    @{ name = 'karpathy-skills';      repo = 'forrestchang/andrej-karpathy-skills' },
    @{ name = 'caveman';              repo = 'JuliusBrussee/caveman' },
    @{ name = 'handoff';              repo = 'thepushkarp/handoff' },
    @{ name = 'ui-ux-pro-max-skill';  repo = 'nextlevelbuilder/ui-ux-pro-max-skill' }
)
foreach ($m in $marketplaces) {
    Write-Host "  - $($m.repo)"
    claude plugin marketplace add $m.repo 2>&1 | Select-Object -Last 1
}

# ---------------------------------------------------------------- 2. 플러그인
Write-Step '플러그인 설치'
$plugins = @(
    'andrej-karpathy-skills@karpathy-skills',
    'caveman@caveman',
    'handoff@handoff',
    'ui-ux-pro-max@ui-ux-pro-max-skill'
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

# ---------------------------------------------------------------- 6. MCP 서버
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
  1. NotebookLM 인증 — 대화형 claude 세션에서 setup_auth 도구를 실행하면
     Chrome 창이 열립니다. Google 계정으로 로그인하면 쿠키가 저장됩니다.
  2. (선택) deep-research 서브에이전트의 권한 프롬프트를 줄이려면
     ~/.claude/settings.json 의 permissions.allow 에
     "WebSearch", "WebFetch", "Glob", "Grep", "Read" 를 추가하세요.
     WebFetch 자동 승인은 임의 URL 접근을 무확인 허용하므로 판단 후 적용하세요.
  3. claude 를 재시작해야 새 스킬/플러그인이 로드됩니다.
'@ -ForegroundColor Yellow
