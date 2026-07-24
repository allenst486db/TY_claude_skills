# TY_claude_skills

개인용 [Claude Code](https://claude.com/claude-code) 스킬 모음. 이 리포는
`~/.claude/skills` 디렉토리를 그대로 담고 있어, 여러 PC에서 동일한 스킬을
동기화해 사용하기 위한 것입니다.

> **핵심 원칙** — 각 PC의 `~/.claude/skills` 디렉토리 자체가 이 리포의 작업본(clone)이
> 되도록 맞춥니다. 그러면 어느 PC에서든 `git pull`로 최신 스킬을 받고,
> 수정·추가 후 `git push`로 올릴 수 있습니다.

## 수록 스킬

| 스킬 | 설명 |
|---|---|
| [`mosikdo-guide`](./mosikdo-guide) | macOS 스타일 HTML 가이드 문서 + 인라인 SVG 모식도 디자인 시스템 |

각 스킬은 `<skill-name>/SKILL.md` 구조를 가집니다.

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
