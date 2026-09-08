#!/usr/bin/env python3
"""nf-metro 0.7.2 산출 SVG 후처리.

nf-metro 가 해 주지 않는 네 가지를 붙인다.

  1) 움직이는 원의 내부 색을 그 원이 따라가는 노선 색과 맞춘다
  2) 애니메이션 속도를 원하는 배수로 올린다
  3) 영역 배지 번호를 흐름 순서로 다시 매긴다
  4) 도면 아래에 "실제 실행 커맨드" 패널을 붙인다 (캔버스를 먼저 늘린다)

사용법
------
    python postprocess_svg.py map.svg map.mmd -o map.final.svg \\
        --panel panel.json --speedup 1.5 --order pre,asm,post,annot,report

`--panel` JSON 형식 (전부 선택):

    {
      "title": "실제 실행 커맨드 — 온프렘",
      "subtitle": "출처: ...",
      "entries": [
        {"name": "Trinity",
         "src": "runTrinity.py:174",
         "cmd": ["Trinity --seqType fq \\\\", "  --left {G}_1.fastq ..."],
         "note": "실측 36h18m · peak 64 GB",
         "warn": false}
      ]
    }

`--panel` 을 주지 않으면 패널 없이 1~3만 적용한다.
`--order` 를 주지 않으면 배지 번호는 건드리지 않는다.

주의: 커맨드 줄은 고정폭 글꼴로 그려진다. 한글은 두 칸을 차지하므로
공백으로 열을 맞추지 말 것 — 어긋난다.
"""
from __future__ import annotations

import argparse
import json
import re
from html import escape
from pathlib import Path

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"
SANS = "'Helvetica Neue', Helvetica, Arial, sans-serif"

PAD_X, COL_GAP, HEAD_H = 60, 40, 54
ENTRY_GAP, TITLE_SIZE, SRC_SIZE = 16, 12.5, 9.5
CMD_SIZE, CMD_LEAD, NOTE_SIZE = 11.0, 14.0, 10.5
GROUP_SIZE, GROUP_GAP = 11.5, 20


# ── 1. 움직이는 원 채색 ───────────────────────────────────────
def parse_line_colors(mmd_path: Path) -> dict[str, str]:
    """`%%metro line:` 선언에서 {노선 id: 색} 을 읽는다."""
    colors: dict[str, str] = {}
    for raw in mmd_path.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s.startswith("%%metro line:"):
            continue
        parts = s[len("%%metro line:"):].split("|")
        if len(parts) >= 3:
            colors[parts[0].strip()] = parts[2].strip()
    return colors


def recolor_balls(svg: str, colors: dict[str, str]) -> tuple[str, int]:
    """원의 fill 을 mpath 가 가리키는 노선 색으로 바꾼다."""
    pat = re.compile(
        r'(<circle r="3\.0"[^>]*?)(fill="#[0-9a-fA-F]{6}")([^>]*>)(.*?)(</circle>)', re.S
    )

    def repl(m: re.Match) -> str:
        head, _fill, tail, body, close = m.groups()
        mp = re.search(r'href="#motion-path-([A-Za-z0-9_]+)-\d+"', body)
        color = colors.get(mp.group(1)) if mp else None
        if not color:
            return m.group(0)
        tail = re.sub(r'stroke="#[0-9a-fA-F]{6}"', 'stroke="#ffffff"', tail)
        tail = re.sub(r'stroke-width="[\d.]+"', 'stroke-width="1.8"', tail)
        tail = re.sub(r'opacity="[\d.]+"', 'opacity="1"', tail)
        return f'{head}fill="{color}"{tail}{body}{close}'

    return pat.subn(repl, svg)


# ── 2. 속도 ───────────────────────────────────────────────────
def speed_up(svg: str, factor: float) -> str:
    if factor == 1:
        return svg
    return re.sub(r'dur="([\d.]+)s"',
                  lambda m: 'dur="%.2fs"' % (float(m.group(1)) / factor), svg)


# ── 3. 영역 번호 ──────────────────────────────────────────────
def renumber_sections(svg: str, order: list[str]) -> tuple[str, int]:
    """배지 번호를 흐름 순서로 다시 매긴다.

    nf-metro 는 그리드 좌표(열→행)로 번호를 매기므로, 아래 행으로 접은 섹션이
    위 행 섹션보다 앞 번호를 받는다. 읽는 사람은 그것을 단계 순서로 읽는다.
    """
    idx = {sid: i for i, sid in enumerate(order, start=1)}
    pat = re.compile(
        r'(<text [^>]*font-size="12"[^>]*data-section-id="(\w+)"[^>]*>)\d+(</text>)'
    )
    return pat.subn(lambda m: m.group(1) + str(idx.get(m.group(2), 0)) + m.group(3), svg)


# ── 5. 역 라벨 부분 채색 ──────────────────────────────────────
def colorize_labels(svg: str, rules: list[dict]) -> tuple[str, int]:
    """역 라벨의 일부 글자만 다른 색으로 칠한다.

    DB 이름을 `uniprot_euk · _pro · _arc · _virus` 처럼 한 역에 모아 놓고
    접미사만 그 DB 를 쓰는 노선 색으로 칠하면, 역을 넷으로 쪼개지 않고도
    "어느 종이 어느 DB 를 쓰는지" 가 읽힌다.

    rules: [{"match": "<라벨 전체>",
             "segments": [["uniprot", null], ["_euk", "#2db572"],
                          ["_pro", ["#f5c542", "#b8860b"]]]}]
    색 자리에 두 개짜리 리스트를 주면 그라디언트를 만든다 (두 노선이 같은 DB 를 쓸 때).
    """
    n = 0
    defs: list[str] = []
    for gi, rule in enumerate(rules):
        label = rule["match"]
        pat = re.compile(r'(<text\b[^>]*>)' + re.escape(escape(label)) + r'(</text>)')
        m = pat.search(svg)
        if not m:
            pat = re.compile(r'(<text\b[^>]*>)' + re.escape(label) + r'(</text>)')
            m = pat.search(svg)
        if not m:
            continue
        spans = []
        for si, (text, color) in enumerate(rule["segments"]):
            if not color:
                spans.append(escape(text))
                continue
            if isinstance(color, (list, tuple)):
                gid = f"seg-grad-{gi}-{si}"
                stops = "".join(
                    f'<stop offset="{o}" stop-color="{c}"/>'
                    for o, c in zip(("0%", "100%"), color)
                )
                defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">{stops}</linearGradient>')
                fill = f"url(#{gid})"
            else:
                fill = color
            spans.append(f'<tspan fill="{fill}" font-weight="700">{escape(text)}</tspan>')
        svg = svg[:m.start()] + m.group(1) + "".join(spans) + m.group(2) + svg[m.end():]
        n += 1
    if defs:
        svg = svg.replace("<defs>", "<defs>\n" + "\n".join(defs), 1)
    return svg, n


# ── 4. 커맨드 패널 ────────────────────────────────────────────

def _text_w(s: str, size: float) -> float:
    """대략적인 렌더 폭. 한글은 한 글자가 ASCII 두 배쯤 된다."""
    return sum(1.0 if ord(c) > 0x2000 else 0.52 for c in s) * size


def _wrap(text: str, size: float, width: float) -> list[str]:
    """주석 한 줄을 칸 폭에 맞춰 접는다. 접지 않으면 옆 칸을 침범한다."""
    out, cur = [], ""
    for word in text.split(" "):
        cand = word if not cur else cur + " " + word
        if _text_w(cand, size) <= width:
            cur = cand
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out or [""]


def _measure(entries: list[dict], col_w: float) -> float:
    h, group = 0.0, None
    for e in entries:
        if e.get("group") and e["group"] != group:
            group = e["group"]
            h += GROUP_GAP + GROUP_SIZE + 8
        h += TITLE_SIZE + 4 + CMD_LEAD * len(e.get("cmd", []))
        if e.get("note"):
            h += (NOTE_SIZE + 3) * len(_wrap(e["note"], NOTE_SIZE, col_w)) + 3
        h += ENTRY_GAP
    return h


def _draw(entries: list[dict], x: float, y: float, col_w: float) -> list[str]:
    out, cy, group = [], y, None
    for e in entries:
        if e.get("group") and e["group"] != group:
            group = e["group"]
            cy += GROUP_GAP + GROUP_SIZE
            out.append(f'<text x="{x:.1f}" y="{cy:.1f}" font-size="{GROUP_SIZE}" '
                       f'font-family="{SANS}" font-weight="700" fill="#2b2b2b" '
                       f'letter-spacing="0.08em">{escape(group.upper())}</text>')
            cy += 6
            out.append(f'<line x1="{x:.1f}" y1="{cy:.1f}" x2="{x + col_w:.1f}" y2="{cy:.1f}" '
                       f'stroke="#c9c9c9" stroke-width="1"/>')
            cy += 2
        cy += TITLE_SIZE
        out.append(f'<text x="{x:.1f}" y="{cy:.1f}" font-size="{TITLE_SIZE}" '
                   f'font-family="{SANS}" font-weight="700" fill="#4a4a4a">'
                   f'{escape(e.get("name", ""))}</text>')
        if e.get("src"):
            out.append(f'<text x="{x + col_w:.1f}" y="{cy:.1f}" font-size="{SRC_SIZE}" '
                       f'font-family="{SANS}" text-anchor="end" fill="#9a9a9a">'
                       f'{escape(e["src"])}</text>')
        cy += 4
        for ln in e.get("cmd", []):
            cy += CMD_LEAD
            out.append(f'<text x="{x:.1f}" y="{cy:.1f}" font-size="{CMD_SIZE}" '
                       f'font-family="{MONO}" fill="#33383d" xml:space="preserve">'
                       f'{escape(ln)}</text>')
        if e.get("note"):
            fill = "#b0392f" if e.get("warn") else "#6f6f6f"
            cy += 3
            for ln in _wrap(e["note"], NOTE_SIZE, col_w):
                cy += NOTE_SIZE + 3
                out.append(f'<text x="{x:.1f}" y="{cy:.1f}" font-size="{NOTE_SIZE}" '
                           f'font-family="{SANS}" fill="{fill}">{escape(ln)}</text>')
        cy += ENTRY_GAP
    return out


def append_panel(svg: str, panel: dict) -> str:
    m = re.search(r'width="(\d+)" height="(\d+)" viewBox="0 0 (\d+) (\d+)"', svg)
    if not m:
        raise SystemExit("SVG 머리말에서 width/height/viewBox 를 찾지 못했습니다.")
    w, h = int(m.group(1)), int(m.group(2))

    entries = panel.get("entries", [])
    col_w = (w - PAD_X * 2 - COL_GAP) / 2

    # 그룹 단위로 묶은 뒤, 두 칸의 높이가 비슷해지는 지점에서 자른다.
    blocks: list[list[dict]] = []
    for e in entries:
        if blocks and e.get("group") == blocks[-1][0].get("group"):
            blocks[-1].append(e)
        else:
            blocks.append([e])
    total = _measure(entries, col_w)
    left, acc = [], 0.0
    cut = len(blocks)
    for i, blk in enumerate(blocks):
        if acc >= total / 2 and i > 0:
            cut = i
            break
        acc += _measure(blk, col_w)
    else:
        cut = len(blocks)
    left = [e for blk in blocks[:cut] for e in blk]
    right = [e for blk in blocks[cut:] for e in blk]
    if not right:
        left, right = entries[: (len(entries) + 1) // 2], entries[(len(entries) + 1) // 2 :]
    panel_h = int(HEAD_H + max(_measure(left, col_w), _measure(right, col_w)) + 26)
    new_h = h + panel_h
    mid = PAD_X + col_w + COL_GAP / 2

    parts = [
        f'<rect x="0" y="{h}" width="{w}" height="{panel_h}" fill="#fbfbfa"/>',
        f'<line x1="{PAD_X}" y1="{h + 0.5}" x2="{w - PAD_X}" y2="{h + 0.5}" '
        f'stroke="#dcdcdc" stroke-width="1"/>',
        f'<text x="{PAD_X}" y="{h + 28}" font-size="15" font-family="{SANS}" '
        f'font-weight="700" fill="#2b2b2b">{escape(panel.get("title", ""))}</text>',
        f'<text x="{PAD_X}" y="{h + 45}" font-size="10.5" font-family="{SANS}" '
        f'fill="#8a8a8a">{escape(panel.get("subtitle", ""))}</text>',
        f'<line x1="{mid:.1f}" y1="{h + HEAD_H - 6}" x2="{mid:.1f}" '
        f'y2="{h + panel_h - 14}" stroke="#e6e6e6" stroke-width="1"/>',
    ]
    parts += _draw(left, PAD_X, h + HEAD_H, col_w)
    parts += _draw(right, PAD_X + col_w + COL_GAP, h + HEAD_H, col_w)

    svg = svg.replace(f'width="{w}" height="{h}" viewBox="0 0 {w} {h}"',
                      f'width="{w}" height="{new_h}" viewBox="0 0 {w} {new_h}"', 1)
    # nf-metro 크레딧을 새 바닥으로 옮긴다
    svg = re.sub(r'(<text x="[\d.]+" y=")[\d.]+(" font-size="8" fill="rgba\(150, 150, 150, 0\.6\)")',
                 lambda mm: mm.group(1) + str(new_h - 8) + mm.group(2), svg)
    return svg.replace("</svg>", "\n".join(parts) + "\n</svg>")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("svg", type=Path, help="nf-metro 가 낸 SVG")
    ap.add_argument("mmd", type=Path, help="같은 지도의 .mmd (노선 색을 읽는다)")
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--panel", type=Path, help="커맨드 패널 JSON")
    ap.add_argument("--speedup", type=float, default=1.5)
    ap.add_argument("--order", help="영역 id 를 흐름 순서로 콤마 나열")
    ap.add_argument("--map-only", type=Path,
                    help="패널 없는 판본을 따로 저장할 경로 (HTML 삽입용)")
    a = ap.parse_args()

    svg = a.svg.read_text(encoding="utf-8")
    svg, n_balls = recolor_balls(svg, parse_line_colors(a.mmd))
    svg = speed_up(svg, a.speedup)

    n_col = 0
    if a.panel:
        _pj = json.loads(a.panel.read_text(encoding="utf-8"))
        if _pj.get("colorize"):
            svg, n_col = colorize_labels(svg, _pj["colorize"])

    n_sec = 0
    if a.order:
        svg, n_sec = renumber_sections(svg, [s.strip() for s in a.order.split(",") if s.strip()])

    if a.map_only:
        a.map_only.write_text(svg, encoding="utf-8")

    n_cmd = 0
    if a.panel and _pj.get("entries"):
        n_cmd = len(_pj["entries"])
        svg = append_panel(svg, _pj)

    a.output.write_text(svg, encoding="utf-8")
    print(f"{a.output}: 원 {n_balls}개 채색 · 속도 {a.speedup}배 · "
          f"영역번호 {n_sec}개 · 라벨 {n_col}개 · 커맨드 {n_cmd}항목")


if __name__ == "__main__":
    main()
