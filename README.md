# TY_claude_skills

개인용 [Claude Code](https://claude.com/claude-code) 스킬 모음. 이 리포는
`~/.claude/skills` 디렉토리를 그대로 담고 있어, 여러 PC에서 동일한 스킬을
동기화해 사용하기 위한 것입니다.

## 수록 스킬

| 스킬 | 설명 |
|---|---|
| [`mosikdo-guide`](./mosikdo-guide) | macOS 스타일 HTML 가이드 문서 + 인라인 SVG 모식도 디자인 시스템 |

## 설치 (새 PC에서 처음 세팅)

`~/.claude/skills` 가 아직 없거나 비어 있는 경우 — 리포를 그 위치로 그대로 clone:

```bash
# macOS / Linux
git clone https://github.com/allenst486db/TY_claude_skills.git ~/.claude/skills
```

```powershell
# Windows (PowerShell)
git clone https://github.com/allenst486db/TY_claude_skills.git "$env:USERPROFILE\.claude\skills"
```

이미 `~/.claude/skills` 에 다른 파일이 있어 clone이 안 되는 경우 — 임시 폴더에
clone 후 내용만 복사하거나, 아래처럼 기존 디렉토리에서 리포를 연결:

```bash
cd ~/.claude/skills
git init && git remote add origin https://github.com/allenst486db/TY_claude_skills.git
git fetch origin && git checkout -f main
```

설치 후 **Claude Code를 새 세션으로 시작**하면 스킬이 로드됩니다.

## 업데이트

```bash
cd ~/.claude/skills
git pull            # 최신본 받기
# 스킬을 수정했다면
git add . && git commit -m "update: <내용>" && git push
```

## 새 스킬 추가

`~/.claude/skills/<skill-name>/SKILL.md` 구조로 폴더를 만들고 커밋·push 하면,
다른 PC에서 `git pull` 로 받아 쓸 수 있습니다.
