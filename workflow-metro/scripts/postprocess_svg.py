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


# ── 6. 우회 노선을 본선 위로 뒤집기 ──────────────────────────
_PATH_D = re.compile(r'\sd="([^"]+)"')


def _iter_d_numbers(d: str):
    """path 의 d 문자열에서 (시작, 끝, 값) 형태로 숫자를 훑는다."""
    for m in re.finditer(r'-?\d+(?:\.\d+)?', d):
        yield m


def mirror_line(svg: str, line_id: str, scale: float = 1.0, tol: float = 4.0) -> tuple[str, int]:
    """한 노선의 곡선을 본선 기준으로 위아래 뒤집는다.

    nf-metro 는 바깥 트랙을 아래로 부풀린다. 우회로를 위로 올리고 싶을 때 쓴다.
    본선 높이(Y0)는 그 노선 경로에 나오는 가장 작은 y 로 잡고, Y0 에서 tol 이내인
    점은 그대로 둔다 — 역·포트와 맞물리는 끝점이 어긋나지 않게 하기 위해서다.

    scale 은 뒤집은 뒤의 진폭이다. 1.0 으로 그대로 뒤집으면 영역 상자 위로 삐져나가는
    일이 잦다 — 위쪽은 역 라벨이 차지하고 있어 여유가 아래보다 좁기 때문이다.
    0.3 안팎으로 낮춰 라벨과 역 사이에 끼워 넣는다.

    M/L/Q/C/S/T 처럼 좌표가 쌍으로 오는 명령만 다룬다. 다른 명령이 있으면 건너뛴다.
    """
    targets = [m for m in re.finditer(
        r'<path[^>]*(?:data-line-id="%s"|id="motion-path-%s-\d+")[^>]*?/?>' % (line_id, line_id), svg)]
    if not targets:
        return svg, 0

    ys: list[float] = []
    for m in targets:
        dm = _PATH_D.search(m.group(0))
        if not dm:
            continue
        if re.search(r'[AaHhVvZzmlqcst]', re.sub(r'-?\d+(?:\.\d+)?', '', dm.group(1))):
            return svg, 0          # 다룰 수 없는 명령이 섞여 있으면 손대지 않는다
        nums = [float(x.group(0)) for x in _iter_d_numbers(dm.group(1))]
        ys += nums[1::2]
    if not ys:
        return svg, 0
    y0 = min(ys)

    def flip(dstr: str) -> str:
        out, last, idx = [], 0, 0
        for m in _iter_d_numbers(dstr):
            out.append(dstr[last:m.start()])
            v = float(m.group(0))
            if idx % 2 == 1 and abs(v - y0) > tol:
                v = y0 - (v - y0) * scale
                out.append(f"{v:.2f}")
            else:
                out.append(m.group(0))
            last, idx = m.end(), idx + 1
        out.append(dstr[last:])
        return "".join(out)

    pieces, prev, n = [], 0, 0
    for m in targets:
        dm = _PATH_D.search(m.group(0))
        if not dm:
            continue
        s = m.start() + dm.start(1)
        e = m.start() + dm.end(1)
        pieces.append(svg[prev:s]); pieces.append(flip(dm.group(1)))
        prev = e; n += 1
    pieces.append(svg[prev:])
    return "".join(pieces), n


# ── 7. 역 하나를 건너뛰는 우회로 그리기 ──────────────────────
def draw_bypass(svg: str, station: str, label: str, colors: dict[str, str],
                lines: list[str], half_w: float = 45.0, height: float = 42.0,
                down: bool = False) -> tuple[str, int]:
    """한 역을 지나치는 우회로를 본선 위에 직접 그린다.

    nf-metro 로는 이 그림이 안 나온다. 같은 노선에 "정차 엣지" 와 "건너뛰는 엣지" 를
    둘 다 걸면 한쪽만 그려지고, 양쪽에 역을 두어 다이아몬드로 만들면 합류점이
    본선 아래로 내려가 뒤 구간 전체가 한 칸씩 처진다. 그래서 직선으로 렌더한 뒤
    우회로만 여기서 얹는다.

    각 노선의 레일 y 를 그 역 근처 수평 선분에서 읽어, 같은 간격을 유지한 채
    위로 부풀린 곡선을 노선 색으로 하나씩 그린다. 역 글리프는 만들지 않는다.
    """
    m = re.search(r'<(?:ellipse|rect|circle)[^>]*data-station-id="%s"[^>]*>' % station, svg)
    if not m:
        return svg, 0
    a = dict(re.findall(r'([a-z-]+)="([^"]*)"', m.group(0)))
    cx = float(a["cx"]) if "cx" in a else float(a["x"]) + float(a["width"]) / 2
    cy = float(a["cy"]) if "cy" in a else float(a["y"]) + float(a["height"]) / 2

    # 노선별 레일 y — 그 역을 가로지르는 수평 선분에서 읽는다
    rail: dict[str, float] = {}
    for pm in re.finditer(r'<path[^>]*data-line-id="([A-Za-z0-9_]+)"[^>]*>', svg):
        lid = pm.group(1)
        if lid not in lines or lid in rail:
            continue
        dm = re.search(r'\sd="M([\d.]+),([\d.]+) L([\d.]+),([\d.]+)"', pm.group(0))
        if not dm:
            continue
        x1, y1, x2, y2 = (float(g) for g in dm.groups())
        if abs(y1 - y2) < 0.6 and min(x1, x2) <= cx <= max(x1, x2):
            rail[lid] = y1
    if not rail:
        return svg, 0

    out, arcs = [], {}
    sign = 1.0 if down else -1.0
    top = (max(rail.values()) + height) if down else (min(rail.values()) - height)
    for lid in lines:
        y = rail.get(lid)
        if y is None:
            continue
        ty = y + sign * height
        x0, x3 = cx - half_w, cx + half_w
        x1, x2 = cx - half_w * 0.34, cx + half_w * 0.34
        c = half_w * 0.30
        d = (f"M{x0:.1f},{y:.1f} C{x0 + c:.1f},{y:.1f} {x1 - c:.1f},{ty:.1f} {x1:.1f},{ty:.1f} "
             f"L{x2:.1f},{ty:.1f} C{x2 + c:.1f},{ty:.1f} {x3 - c:.1f},{y:.1f} {x3:.1f},{y:.1f}")
        arcs[lid] = d
        out.append(f'<path d="{d}" stroke="{colors[lid]}" stroke-width="4.0" fill="none" '
                   f'stroke-linecap="round" stroke-linejoin="round" class="metro-bypass"/>')
    ly = top + 16 if down else top - 3
    out.append(f'<text x="{cx:.1f}" y="{ly:.1f}" font-size="13" font-family="{SANS}" '
               f'font-weight="bold" fill="#333333" text-anchor="middle" paint-order="stroke" '
               f'stroke="#ffffff" stroke-width="3">{escape(label)}</text>')

    # 우회로를 위로 그릴 때만 역 라벨을 아래로 비켜 준다
    if not down:
        def move(mm):
            attrs = mm.group(1)
            if float(dict(re.findall(r'([a-z-]+)="([^"]*)"', attrs)).get("y", 0)) < cy:
                attrs = re.sub(r'y="[\d.]+"', 'y="%.1f"' % (cy + 26), attrs)
            return "<text " + attrs + ">"
        svg = re.sub(r'<text ([^>]*data-station-id="%s"[^>]*)>' % station, move, svg)

    dur = re.search(r'dur="([\d.]+)s"', svg)
    if dur:
        for i, lid in enumerate(k for k in lines if k in rail):
            pid = f"bypass-{station}-{lid}"
            out.append(f'<path id="{pid}" d="{arcs[lid]}" fill="none" stroke="none"/>')
            out.append(
                f'<circle r="3.0" fill="{colors[lid]}" opacity="1" stroke="#ffffff" stroke-width="1.8">'
                f'<animateMotion dur="{dur.group(1)}s" repeatCount="indefinite" '
                f'begin="{i * 0.7:.2f}s"><mpath href="#{pid}"/></animateMotion></circle>')
    return svg.replace("</svg>", "\n".join(out) + "\n</svg>"), len(out) - 1


# ── 8. 한 영역 안에서 하위 묶음을 옅은 음영으로 표시 ─────────
def _station_box(svg: str, sid: str):
    """역 글리프의 (x, y) 와 그 역 라벨의 가로 폭을 돌려준다."""
    m = re.search(r'<(?:ellipse|rect|circle)[^>]*data-station-id="%s"[^>]*>' % sid, svg)
    if not m:
        return None
    a = dict(re.findall(r'([a-z-]+)="([^"]*)"', m.group(0)))
    x = float(a["cx"]) if "cx" in a else float(a["x"]) + float(a["width"]) / 2
    y = float(a["cy"]) if "cy" in a else float(a["y"]) + float(a["height"]) / 2
    w = 60.0
    lm = re.search(r'<text ([^>]*data-station-id="%s"[^>]*)>([^<]*)</text>' % sid, svg)
    if lm:
        fs = float(dict(re.findall(r'([a-z-]+)="([^"]*)"', lm.group(1))).get("font-size", 13))
        w = max(w, _text_w(lm.group(2), fs) + 12)
    return x, y, w


def shade_groups(svg: str, groups: list[tuple[str, list[str]]],
                 pad: float = 16.0, gap_factor: float = 1.7,
                 min_h: float = 0.0) -> tuple[str, int]:
    """영역 하나 안에서 같은 성격의 역들을 옅은 음영으로 묶는다.

    큰 상자를 여러 개로 쪼개면 그 상자에 정차하지 않는 노선이 우회 차선으로
    그려진다(§6-2). 상자는 하나로 두고 안에서만 묶어 보이게 하는 방법이다.

    한 묶음의 역들이 서로 다른 층(x)에 있거나 세로로 떨어져 있으면 덩어리마다
    사각형을 하나씩 그리고 라벨은 가장 큰 덩어리에만 붙인다.
    """
    # 음영은 노선보다 뒤에 깔려야 한다 — 마지막 영역 상자 뒤에 끼워 넣는다.
    anchor = None
    for m in re.finditer(r'<rect[^>]*class="nf-metro-section-box"[^>]*/?>', svg):
        anchor = m.end()
    if anchor is None:
        return svg, 0

    out, top_out, n = [], [], 0
    for label, sids in groups:
        pts = [(sid, _station_box(svg, sid)) for sid in sids]
        pts = [(s, b) for s, b in pts if b]
        if not pts:
            continue
        by_x: dict[float, list] = {}
        for s, (x, y, w) in pts:
            by_x.setdefault(round(x, 1), []).append((y, w))
        clusters = []
        for x, ys in by_x.items():
            ys.sort()
            span = [ys[0]]
            step = 68.0
            for cur in ys[1:]:
                if cur[0] - span[-1][0] > step * gap_factor:
                    clusters.append((x, span)); span = [cur]
                else:
                    span.append(cur)
            clusters.append((x, span))
        biggest = max(clusters, key=lambda c: len(c[1]))
        for x, span in clusters:
            w = max(v[1] for v in span)
            y0, y1 = span[0][0], span[-1][0]
            rx0, ry0 = x - w / 2 - pad - 16, y0 - pad - 6   # 왼쪽에 묶음 이름 자리
            rw = w + pad * 2 + 20
            rh = (y1 - y0) + pad * 2 + 24
            # 세로로 세운 묶음 이름이 들어갈 높이를 확보한다
            need = _text_w(label, 11) + 24
            if rh < max(need, min_h):
                grow = max(need, min_h) - rh
                ry0 -= grow / 2
                rh += grow
            out.append(f'<rect x="{rx0:.1f}" y="{ry0:.1f}" width="{rw:.1f}" height="{rh:.1f}" '
                       f'rx="8" ry="8" fill="#1b2027" opacity="0.075" '
                       f'stroke="#9aa3ad" stroke-opacity="0.35" stroke-width="1"/>')
            if span is biggest[1]:
                # 역 이름과 겹치지 않게, 음영 안쪽 왼쪽 가장자리에 세로로 세운다
                top_out.append(
                    f'<text x="{rx0 + 11:.1f}" y="{ry0 + rh / 2:.1f}" font-size="11" '
                    f'font-family="{SANS}" font-weight="700" fill="#7a828c" '
                    f'letter-spacing="0.1em" text-anchor="middle" '
                    f'transform="rotate(-90 {rx0 + 11:.1f} {ry0 + rh / 2:.1f})" '
                    f'paint-order="stroke" stroke="#ffffff" stroke-width="3.5">'
                    f'{escape(label.upper())}</text>')
            n += 1
    svg = svg[:anchor] + "\n" + "\n".join(out) + svg[anchor:]
    return svg.replace("</svg>", "\n".join(top_out) + "\n</svg>"), n


# ── 9. 공이 지나지 않는 갈래에 공 추가 ───────────────────────
def animate_through(svg: str, station: str, colors: dict[str, str],
                    lines: list[str]) -> tuple[str, int]:
    """그 역을 지나는 움직이는 원이 하나도 없을 때 직접 만들어 붙인다.

    nf-metro 는 노선마다 몇 개의 경로에만 공을 붙인다. 분기가 많으면 어떤 갈래는
    공이 한 번도 지나가지 않는다. 그 역에 들어오는 선분과 나가는 선분을 이어
    경로를 만들고 공을 하나 태운다.
    """
    m = re.search(r'<(?:ellipse|rect|circle)[^>]*data-station-id="%s"[^>]*>' % station, svg)
    if not m:
        return svg, 0
    a = dict(re.findall(r'([a-z-]+)="([^"]*)"', m.group(0)))
    cx = float(a["cx"]) if "cx" in a else float(a["x"]) + float(a["width"]) / 2
    cy = float(a["cy"]) if "cy" in a else float(a["y"]) + float(a["height"]) / 2

    def ends(d):
        n = [float(v) for v in re.findall(r'-?\d+(?:\.\d+)?', d)]
        pts = list(zip(n[0::2], n[1::2]))
        return pts[0], pts[-1]

    incoming: dict[str, str] = {}
    outgoing: dict[str, str] = {}
    for pm in re.finditer(r'<path[^>]*data-line-id="([A-Za-z0-9_]+)"[^>]*>', svg):
        lid = pm.group(1)
        if lid not in lines:
            continue
        dm = re.search(r'\sd="([^"]+)"', pm.group(0))
        if not dm:
            continue
        (sx, sy), (ex, ey) = ends(dm.group(1))
        if abs(ex - cx) < 9 and abs(ey - cy) < 9 and lid not in incoming:
            incoming[lid] = dm.group(1)
        if abs(sx - cx) < 9 and abs(sy - cy) < 9 and lid not in outgoing:
            outgoing[lid] = dm.group(1)

    dur = re.search(r'dur="([\d.]+)s"', svg)
    if not dur:
        return svg, 0
    out, n = [], 0
    for i, lid in enumerate(lines):
        if lid not in incoming or lid not in outgoing:
            continue
        tail = re.sub(r'^M', 'L', outgoing[lid].strip())
        d = incoming[lid] + " " + tail
        pid = f"through-{station}-{lid}"
        out.append(f'<path id="{pid}" d="{d}" fill="none" stroke="none"/>')
        out.append(
            f'<circle r="3.0" fill="{colors[lid]}" opacity="1" stroke="#ffffff" stroke-width="1.8">'
            f'<animateMotion dur="{dur.group(1)}s" repeatCount="indefinite" '
            f'begin="{i * 0.9:.2f}s"><mpath href="#{pid}"/></animateMotion></circle>')
        n += 1
    if not out:
        return svg, 0
    return svg.replace("</svg>", "\n".join(out) + "\n</svg>"), n


# ── 10. 역 라벨을 두 줄로 ─────────────────────────────────────
def split_label(svg: str, station: str, sep: str = " (",
                above: bool = False) -> tuple[str, int]:
    """긴 역 이름을 두 줄로 쪼갠다. 한 줄로 두면 옆 역 라벨과 붙는다.

    above 를 주면 역 위쪽에 올린다 — 아래에 우회로를 그릴 때 자리를 비켜 주기 위해서다.
    """
    m = re.search(r'<text ([^>]*data-station-id="%s"[^>]*)>([^<]*)</text>' % station, svg)
    if not m or sep not in m.group(2):
        return svg, 0
    a = dict(re.findall(r'([a-z-]+)="([^"]*)"', m.group(1)))
    x = a.get("x", "0")
    # 두 줄로 벌리면 아래 줄이 레일 위로 내려앉는다. 전체를 올린다.
    box = _station_box(svg, station)
    if above and box:
        newy = box[1] - 46.0
    else:
        newy = float(a.get("y", 0)) - 8
    attrs = re.sub(r'y="[\d.]+"', 'y="%.1f"' % newy, m.group(1))
    head, _, tail = m.group(2).partition(sep)
    body = (f'<tspan x="{x}" dy="-0.55em">{escape(head)}</tspan>'
            f'<tspan x="{x}" dy="1.15em">{escape(sep.strip() + tail)}</tspan>')
    return svg[:m.start()] + "<text " + attrs + ">" + body + "</text>" + svg[m.end():], 1


# ── 4. 커맨드 패널 ────────────────────────────────────────────

def _text_w(s: str, size: float) -> float:
    """대략적인 렌더 폭. 한글은 한 글자가 ASCII 두 배쯤 된다."""
    return sum(1.0 if ord(c) > 0x2000 else 0.52 for c in s) * size


def _src_wraps(entry: dict, col_w: float) -> bool:
    """항목 이름과 오른쪽 정렬한 출처가 한 줄에 같이 들어가는지."""
    if not entry.get("src"):
        return False
    need = _text_w(entry.get("name", ""), TITLE_SIZE) + _text_w(entry["src"], SRC_SIZE) + 28
    return need > col_w


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
        if _src_wraps(e, col_w):
            h += SRC_SIZE + 3
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
            # 이름이 길면 오른쪽 정렬한 출처와 겹친다. 그럴 때만 다음 줄로 내린다.
            if _src_wraps(e, col_w):
                cy += SRC_SIZE + 3
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
    ap.add_argument("--animate-through", action="append", default=[],
                    help="역id — 그 역을 지나는 공이 없을 때 직접 만들어 붙인다.")
    ap.add_argument("--split-label", action="append", default=[],
                    help="역id[:구분자] — 역 이름을 두 줄로 쪼갠다 (기본 구분자 \" (\").")
    ap.add_argument("--group", action="append", default=[],
                    help="라벨:역id1,역id2,... — 한 영역 안에서 같은 성격의 역을 옅은 음영으로 묶는다.")
    ap.add_argument("--bypass", action="append", default=[],
                    help="역id:라벨[:반폭:높이] — 그 역을 건너뛰는 우회로를 본선 위에 그린다.")
    ap.add_argument("--mirror-line", action="append", default=[],
                    help="ID[:배율] — 이 노선의 곡선을 본선 위로 뒤집는다 (우회로 표현). 배율 기본 1.0.")
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

    n_thr = 0
    for sid in a.animate_through:
        cols = parse_line_colors(a.mmd)
        svg, k = animate_through(svg, sid, cols, [c for c in cols if c != 'reuse'])
        n_thr += k
    for spec in a.split_label:
        bits = spec.split(':')
        sid = bits[0]
        sep = bits[1] if len(bits) > 1 and bits[1] else ' ('
        svg, _k = split_label(svg, sid, sep, len(bits) > 2 and bits[2].strip() == 'above')

    n_grp = 0
    if a.group:
        gs = [(g.split(':', 1)[0], g.split(':', 1)[1].split(',')) for g in a.group]
        svg, n_grp = shade_groups(svg, gs)

    n_by = 0
    for spec in a.bypass:
        parts_ = spec.split(':')
        st, lab = parts_[0], parts_[1]
        hw = float(parts_[2]) if len(parts_) > 2 else 45.0
        hh = float(parts_[3]) if len(parts_) > 3 else 42.0
        dn = len(parts_) > 4 and parts_[4] == "down"
        cols = parse_line_colors(a.mmd)
        ids = [k for k in cols if k not in ('reuse',)]
        svg, k = draw_bypass(svg, st, lab, cols, ids, hw, hh, dn)
        n_by += k

    n_mir = 0
    for spec in a.mirror_line:
        lid, _, sc = spec.partition(":")
        svg, k = mirror_line(svg, lid, float(sc) if sc else 1.0)
        n_mir += k

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
          f"영역번호 {n_sec}개 · 묶음 {n_grp}개 · 우회 {n_by}선 · 추가공 {n_thr}개 · 커맨드 {n_cmd}항목")


if __name__ == "__main__":
    main()
