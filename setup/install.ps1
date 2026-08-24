# setup/install.ps1 — Windows 편의 래퍼. 실제 작업은 install.mjs 가 한다.
#
#   pwsh -File setup/install.ps1 --dry-run
#   pwsh -File setup/install.ps1

$ErrorActionPreference = 'Stop'
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw 'Node.js 18+ 가 필요합니다.'
}
& node (Join-Path $PSScriptRoot 'install.mjs') @args
exit $LASTEXITCODE
