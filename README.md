# TY_claude_skills

개인용 [Claude Code](https://claude.com/claude-code) 스킬 모음. 이 리포는
`~/.claude/skills` 디렉토리를 그대로 담고 있어, 여러 PC에서 동일한 스킬을
동기화해 사용하기 위한 것입니다.

> **핵심 원칙** — 각 PC의 `~/.claude/skills` 디렉토리 자체가 이 리포의 작업본(clone)이
> 되도록 맞춥니다. 그러면 어느 PC에서든 `git pull`로 최신 스킬을 받고,
> 수정·추가 후 `git push`로 올릴 수 있습니다.

## 📘 시각 가이드 (권장)

동기화 구조와 절차를 **모식도**로 정리한 macOS 스타일 가이드가 있습니다. 아래 내용과
동일하지만 훨씬 읽기 좋습니다.

- **바로 보기 (GitHub Pages)** → **https://allenst486db.github.io/TY_claude_skills/**
- **소스** → [`docs/guide.html`](./docs/guide.html) (내려받아 브라우저로 열어도 됩니다)
- **전체 스택 재현 가이드** → [`docs/stack-guide.html`](./docs/stack-guide.html)
  — 스킬뿐 아니라 **플러그인·MCP 서버까지** 한 번에 옮기는 방법 ([5번](#5-전체-스택-재현-플러그인--mcp-포함) 참고)

> GitHub의 README는 마크다운만 렌더링해 CSS·SVG가 제거되므로, 스타일이 적용된 가이드는
> HTML 문서로 제공하고 GitHub Pages로 호스팅합니다. 아래 마크다운 절차만 따라도 동일하게
> 세팅됩니다.

<details>
<summary>GitHub Pages 최초 1회 켜는 방법</summary>

1. 리포 → **Settings** → 좌측 **Pages**
2. **Build and deployment** → **Source** = `Deploy from a branch`
3. **Branch** = `main`, 폴더 = `/ (root)` → **Save**
4. 1~2분 뒤 위 Pages 주소가 활성화됩니다. (루트 주소는 가이드로 자동 이동)

</details>

## 수록 스킬

| 스킬 | 설명 |
|---|---|
| [`mosikdo-guide`](./mosikdo-guide) | macOS 스타일 HTML 가이드 문서 + 인라인 SVG 모식도 디자인 시스템. 좌측 목차(접기/펼치기, 클릭 이동)와 코드블록 복사 버튼 기본 내장 ([상세](./mosikdo-guide/references/toc-and-copy.md)) |
| [`release-note-docx`](./release-note-docx) | 버전별 갱신 이력을 담은 Word(.docx) 릴리스 노트 빌더. 개요(제목·메타·요약 표)와 버전별 상세(큰 버전 헤더·색상 라벨 불릿·비교표)를 결합한 docx-js 라이브러리 ([상세](./release-note-docx/references/style-spec.md)) |

각 스킬은 `<skill-name>/SKILL.md` 구조를 가집니다.

> 위 표는 **이 리포에 직접 담긴** 자체 제작 스킬입니다. 남의 저장소에서 가져다 쓰는 스킬 20종은
> 파일을 복사해 두지 않고 [`setup/claude-stack.json`](./setup/claude-stack.json)에 **출처와 고정 커밋만**
> 기록해 둡니다. 설치는 [5번](#5-전체-스택-재현-플러그인--mcp-포함)의 스크립트가 처리합니다.

---

## 1. 새 PC에서 처음 설치하기

### 경우 A — `~/.claude/skills` 가 없거나 비어 있음 (가장 간단)

리포를 그 위치로 그대로 clone 합니다.

```bash
# macOS / Linux
git clone https://github.com/allenst486db/TY_claude_skills.git ~/.claude/skills
```
```powershell
# Windows (PowerShell)
git clone https://github.com/allenst486db/TY_claude_skills.git "$env:USERPROFILE\.claude\skills"
```

### 경우 B — 그 PC에 이미 로컬 스킬이 들어 있음

기존 스킬을 **보존하면서** 리포에 연결하고, 그 PC에만 있던 스킬은 리포로 함께
올립니다. (아래 [2번](#2-다른-pc의-기존-스킬을-이-리포에-추가하기) 절차를 따르세요.)

설치 후에는 **Claude Code를 새 세션으로 시작**해야 스킬이 로드됩니다.

---

## 2. 다른 PC의 기존 스킬을 이 리포에 추가하기

이미 `~/.claude/skills` 에 로컬 스킬이 있는 PC를, 리포와 합치는 방법입니다.
서로 다른 이름의 스킬 폴더는 충돌 없이 그대로 합쳐집니다.

```bash
cd ~/.claude/skills                    # Windows: cd "$env:USERPROFILE\.claude\skills"

# 1) 이 폴더를 git 저장소로 초기화하고 로컬 스킬을 먼저 커밋
git init -b main
git add -A
git commit -m "local skills from <이-PC-이름>"

# 2) 원격 리포 연결 후 내려받아 병합 (서로 다른 뿌리이므로 --allow-unrelated-histories 필요)
git remote add origin https://github.com/allenst486db/TY_claude_skills.git
git fetch origin
git merge origin/main --allow-unrelated-histories -m "merge TY_claude_skills"

# 3) 합쳐진 결과(로컬 스킬 + 리포 스킬)를 올림
git push -u origin main
```

이후 이 PC의 `~/.claude/skills` 도 리포의 작업본이 되어, 다른 PC와 동일하게
`pull`/`push` 로 관리됩니다.

> **충돌이 나는 경우** — 두 PC가 *같은 이름*의 스킬 폴더를 서로 다른 내용으로
> 가지고 있으면 `git merge` 가 해당 파일에서 충돌을 표시합니다. 파일을 열어
> 남길 내용을 정리한 뒤 `git add <파일> && git commit` 으로 마무리하고 `push` 하세요.

### 대안 — 병합이 번거로울 때 (임시 clone 후 복사)

git 병합이 부담스러우면, 리포를 임시 폴더에 clone → 올리고 싶은 스킬 폴더만
복사 → commit/push 하는 방식도 됩니다.

```bash
git clone https://github.com/allenst486db/TY_claude_skills.git /tmp/ty_skills
cp -r ~/.claude/skills/<올릴-스킬> /tmp/ty_skills/
cd /tmp/ty_skills && git add -A && git commit -m "add <올릴-스킬>" && git push
```
```powershell
# Windows (PowerShell)
git clone https://github.com/allenst486db/TY_claude_skills.git "$env:TEMP\ty_skills"
Copy-Item "$env:USERPROFILE\.claude\skills\<올릴-스킬>" "$env:TEMP\ty_skills\" -Recurse -Force
Set-Location "$env:TEMP\ty_skills"; git add -A; git commit -m "add <올릴-스킬>"; git push
```

단, 이 방식은 그 PC의 `~/.claude/skills` 를 리포 작업본으로 만들지는 않으므로,
그 PC에서도 계속 관리하려면 [경우 A](#경우-a--claudeskills-가-없거나-비어-있음-가장-간단) 또는
[2번 병합 방식](#2-다른-pc의-기존-스킬을-이-리포에-추가하기)으로 한 번 연결해 두는 것이 좋습니다.

---

## 3. 평상시 관리 (모든 PC 공통)

```bash
cd ~/.claude/skills                    # Windows: cd "$env:USERPROFILE\.claude\skills"

git pull                               # 다른 PC에서 올린 최신 스킬 받기

# 스킬을 수정하거나 새로 만든 뒤
git add -A
git commit -m "update: <내용>"
git push
```

- **작업 시작 전 `git pull`, 끝나고 `git push`** 를 습관화하면 PC 간 충돌이 거의 없습니다.
- 여러 PC에서 같은 스킬을 동시에 고쳐 충돌이 나면, 위 [충돌 안내](#2-다른-pc의-기존-스킬을-이-리포에-추가하기)와 동일하게
  파일을 정리한 뒤 커밋하면 됩니다.

## 4. 새 스킬 추가

`~/.claude/skills/<skill-name>/SKILL.md` 구조로 폴더를 만들고 커밋·push 하면,
다른 PC에서 `git pull` 로 받아 쓸 수 있습니다. `SKILL.md` 의 `name` 은 폴더명과
같게, `description` 에는 "언제 이 스킬을 쓰는지"를 구체적으로 적어야 잘 발동합니다.

남의 저장소 스킬을 스택에 편입할 때는 파일을 복사하지 말고
[`setup/claude-stack.json`](./setup/claude-stack.json) 의 `externalSkills` 에
`name`·`repo`·`path` 를 적고 `pinnedCommits` 에 그 저장소의 커밋 SHA 를 추가합니다.

---

## 5. 전체 스택 재현 (플러그인 · MCP 포함)

위 1~4번은 **스킬 폴더**를 동기화하는 방법입니다. 플러그인과 MCP 서버는 파일이 아니라
`claude` CLI 로 등록되므로 git 만으로는 따라오지 않습니다.
[`setup/claude-stack.json`](./setup/claude-stack.json) 이 그 전부(스킬 21종 · 플러그인 6종 ·
MCP 서버 2종)를 담고 있고, `setup/install.mjs` 가 그대로 재현합니다.

> 동기화하지 않기로 한 스킬은 매니페스트의 `localOnlySkills` 에 기록만 해 둡니다.
> 설치 스크립트는 이 항목을 건드리지 않으므로, 해당 스킬은 PC 마다 수동으로 옮겨야 합니다.

```bash
# 새 PC — 리포를 skills 디렉터리로 clone 한 경우
node ~/.claude/skills/setup/install.mjs --dry-run   # 무엇을 할지만 출력
node ~/.claude/skills/setup/install.mjs             # 실제 실행
```
```powershell
# Windows
pwsh -File "$env:USERPROFILE\.claude\skills\setup\install.ps1" --dry-run
pwsh -File "$env:USERPROFILE\.claude\skills\setup\install.ps1"
```

이미 로컬 스킬이 있어 skills 디렉터리를 통째로 clone 할 수 없는 PC라면, 리포를 아무 데나
받아서 스크립트만 실행하면 됩니다 — 기존 스킬은 건드리지 않고 없는 것만 채웁니다.

### 안전 규칙 — 기존 것을 잃지 않습니다

| 상황 | 동작 |
|---|---|
| 폴더가 없음 | **설치** |
| 내용이 같음 (폴더 전체 SHA-256 비교) | **건너뜀** |
| 내용이 다름 | `<이름>.bak-<타임스탬프>` 로 **백업한 뒤 교체** |
| 심볼릭 링크임 | **건너뜀** (다른 도구가 관리 중) |

파일을 지우는 경로가 없습니다. 백업 폴더는 자동으로 삭제되지 않으니 확인 후 직접 지우세요.

### 버전 고정

`pinnedCommits` 에 저장소별 커밋 SHA 를 박아 두어 **모든 PC가 같은 버전**을 받습니다.
최신으로 올리려면 `--latest` 로 실행해 확인한 뒤, 잘 돌면 그 SHA 로 매니페스트를 갱신해 커밋합니다.

```bash
node setup/install.mjs --latest --dry-run   # 무엇이 바뀌는지
node setup/install.mjs --latest             # 적용
git ls-remote https://github.com/heygen-com/hyperframes.git HEAD   # 새 SHA 확인
```

부분 실행 플래그: `--skills` · `--plugins` · `--mcp`

### 스크립트가 못 하는 것

- **NotebookLM 인증** — 대화형 `claude` 세션에서 `setup_auth` 실행 → Chrome 에서 Google 로그인 (PC당 1회)
- **claude.ai 커넥터** (Notion·Figma·Gamma 등) — 계정 단위라 로그인하면 자동으로 따라옵니다
- **Claude Code 재시작** — 새 스킬·플러그인은 재시작해야 로드됩니다

자세한 설명과 모식도는 [`docs/stack-guide.html`](./docs/stack-guide.html) 에 있습니다.
