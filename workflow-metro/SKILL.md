---
name: workflow-metro
description: 파이프라인/워크플로우를 nf-core 스타일 지하철 노선도(metro map) SVG로 그린다. 사용자가 "metro map", "메트로맵", "노선도", "워크플로우 다이어그램", "파이프라인 다이어그램", "nf-core 스타일 다이어그램"을 요청하거나, 여러 설정 조합(kingdom, mapper × quantifier 등)이 각각 하나의 색 노선으로 표현되는 분석 워크플로우를 그림으로 정리하려 할 때 사용한다. 옵션 경로가 점선으로 갈라지고 구간(섹션)별로 묶이는 다단계 파이프라인 도식에 적합하다. 단순 박스-화살표 순서도나 개념 모식도는 svg-infographic / mosikdo-guide 를 쓴다.
---

# Workflow metro map

노선도는 손으로 SVG를 쓰지 않는다. 렌더러 **`nf-metro`** 가 Mermaid 유사 `.mmd` → SVG 레이아웃을 전부 계산한다.
당신이 할 일은 **`.mmd` 스펙을 정확히 쓰는 것**과, 렌더 뒤 **몇 가지를 후처리하는 것**뿐이다.

> 스킬 이름(`workflow-metro`)과 렌더러 이름(`nf-metro`)은 다르다. 커맨드는 항상 `nf-metro` 다.

## 0. 설치와 버전

```bash
python -m nf_metro --version || pip install nf-metro
```

**이 문서는 실제 동작을 확인한 0.7.2 기준이다.** 이전 판 문서에 있던
`%%metro animate:` `%%metro caption:` `%%metro group:` `%%metro marker:`,
`validate-svg` 서브커맨드, `--line-spread` `--fold-threshold` `--inactive-lines`
`--mode` `--no-chrome-css` 플래그는 **0.7.2에 없다.** 쓰면 조용히 무시되거나 에러가 난다.
아래 §5에 실제 존재하는 디렉티브·플래그를 전부 적어 두었다.

홈에 못 깔면 `--target` 으로 아무 데나 깔고 `PYTHONPATH` 로 잡는다 (공용 서버에서 유용):

```bash
pip install --target /path/to/pylib nf-metro
PYTHONPATH=/path/to/pylib /path/to/pylib/bin/nf-metro render map.mmd -o map.svg
```

Windows + 한글 라벨이면 **반드시** `PYTHONUTF8=1` (없으면 cp949 UnicodeDecodeError).

## 1. 먼저 사실을 모은다 (그리기 전)

`.mmd`를 쓰기 전에 아래를 확정한다. 모르면 코드/설정을 읽는다 — 추측해서 그리면 **틀린 노선도**가 나온다.
틀린 노선도는 없는 것보다 나쁘다. 보는 사람이 그것을 사실로 믿기 때문이다.

1. **구간(section)** — 전처리 / 조립 / 정량 / 주석 / 결과 같은 단계 묶음
2. **노선(line)** — **하나를 고르면 나머지가 따라 정해지는 축**. §6 참조
3. **역(station)** — 각 도구·프로세스. 한 역을 여러 노선이 지나면 굵기가 자동으로 커진다
4. **분기점** — 같은 노선 안에서 갈렸다 합류하는 곳 (택일 도구, 그룹 구성 옵션 등)
5. **옵션 경로** — 기본 off 인 경로 → `dashed` 노선
6. **입출력 파일** — 시작 FASTQ, 끝 XLSX 등 → `%%metro file:`

## 2. `.mmd` 작성

`examples/` 의 파일을 복사해 고치는 게 가장 빠르다. 구조:

```
%%metro title: T2_Denovo
%%metro style: light                    # light | dark
%%metro legend: bl                      # tl tr bl br bottom right none
%%metro line: <id> | <범례 텍스트> | <#색상> [| solid|dashed|dotted]
%%metro file: <station_id> | FASTQ [| 캡션]
%%metro grid: <section> | col,row[,rowspan[,colspan]]

graph LR
    subgraph pre [전처리]
        %%metro exit: bottom | line_a,line_b
        fastq[FASTQ]
        trim[Trimmomatic]
        fastq -->|line_a,line_b| trim
    end
    subgraph align [정렬]
        trim -->|line_a| hisat          # 섹션 간 엣지도 여기 써도 된다
    end
```

핵심 규칙:

- 엣지의 `|...|`에는 **그 구간을 지나는 모든 노선 id**를 콤마로 적는다. 빠뜨리면 노선이 끊긴다.
- **분기(fork-join)는 같은 노선 id를 여러 엣지에 걸면 된다.** 앞 역에서 여러 역으로 각각
  엣지를 내고, 그 역들에서 다시 같은 뒤 역으로 모으면 색이 갈렸다 합류한다.
- 배치는 자동(topological). 마음에 안 들 때만 `%%metro grid:` 로 고정한다.
- 색은 참조 팔레트를 재사용: `#2db572` `#0570b0` `#f5c542` `#a05fb4` `#e63946` `#ff8c00`, 옵션 점선 `#9e9e9e`.

## 3. 렌더

```bash
nf-metro validate map.mmd                                   # 스펙 오류
nf-metro info     map.mmd                                   # 섹션/노선/역 요약으로 사실 대조
nf-metro render   map.mmd -o map.svg --theme light --animate
```

렌더 후 **반드시 눈으로 확인한다.** 로컬 SVG는 헤드리스 브라우저로 PNG를 굽는 게 가장 확실하다:

```bash
chrome --headless --disable-gpu --screenshot=map.png \
       --window-size=<W>,<H> --default-background-color=ffffff file:///abs/path/map.svg
```

`<W>` `<H>` 는 SVG의 `width=` `height=` 를 그대로 쓴다.

**라벨 겹침은 눈으로만 잡지 말고 기계로 센다.** `<text>` 의 x/y/font-size/text-anchor로
사각형을 만들어 교차를 세는 20줄짜리 스크립트면 충분하다. 폭 추정에서 한글은 1.0em,
ASCII는 0.58em 으로 잡아야 맞는다 — 한글을 ASCII 폭으로 재면 겹침을 못 잡는다.
목표는 **겹침 0** 이다.

레이아웃이 어긋나면 이 순서로 조정:
`--x-spacing/--y-spacing` → `--max-layers-per-row` → `%%metro exit:/entry:` 포트 힌트 →
마지막에 `%%metro grid:` 수동 고정.

**한 방향으로 흐르게 하려면** 섹션을 전부 같은 행에 두고(`grid: <sec> | <n>,0`)
각 섹션에 `entry: left` / `exit: right` 를 준다. 아래 행으로 접으면 nf-metro 는
되돌아오는 방향(RL)으로 그리는데, 읽는 사람은 그것을 역행으로 읽는다.
영역이 많아 한 행에 안 들어가면 **접기 전에 역을 줄이는 쪽**을 먼저 검토한다.

## 4. 렌더 뒤 후처리 — nf-metro 가 안 해 주는 것

세 가지는 SVG를 직접 손봐야 한다. 스크립트 하나로 묶어 두면 재렌더마다 바로 다시 적용된다.

**(a) 움직이는 원에 노선 색 입히기.** `--animate` 가 만드는 원은 흰색 고정이다.
따라가는 경로 id가 노선 id를 담고 있으므로 그걸로 색을 찾는다.

```
<circle r="3.0" fill="#ffffff" ...><animateMotion ...><mpath href="#motion-path-<lineid>-<n>"/>
→ fill 을 노선 색으로, stroke 를 #ffffff 로
```

**(b) 애니메이션 속도.** `dur="<초>s"` 를 원하는 배수로 나눈다. 기본은 대체로 느리다.

nf-metro 는 **모든 공에 같은 `dur` 을 주고 `keyTimes` 로 실제 이동 구간을 나눈다** —
경로가 길수록 `keyTimes` 가 커져 속도가 같아지고, `begin` 은 전부 0 이다.
공을 새로 얹을 때도 이 규칙을 따라야 한다. `begin` 을 어긋나게 주거나 `keyTimes` 를 빼면
혼자 늦게 출발하거나 혼자 빠르게 움직여 눈에 띈다.
`add_ball()` 이 기존 공에서 속도를 역산해 맞춘다.

**(c) 하단 커맨드 패널.** 실제 커맨드는 옅은 배경의 코드블럭 안에, 설명·주석은 그 밖에 둔다.
섞어 놓으면 무엇이 실행되는 줄인지 한눈에 안 들어온다. 참조 도면처럼 "실제 실행 커맨드" 블록을 붙이려면
`</svg>` 앞에 `<rect>`+`<text>` 를 직접 추가하고 `height`/`viewBox` 를 그만큼 늘린다.
본문 폰트는 `'Helvetica Neue', Helvetica, Arial, sans-serif`,
커맨드는 `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace` 9~9.5px.
**고정폭 글꼴에서 한글은 두 칸을 차지한다** — 공백으로 열을 맞추면 어긋나므로 정렬하지 말 것.

**(d) 영역 번호.** 배지 번호는 그리드 좌표(열→행)순이라, 아래 행으로 접은 섹션이
위 행 섹션보다 앞 번호를 받는다. 읽는 사람은 그것을 단계 순서로 읽으므로
`data-section-id` 를 보고 흐름 순서로 다시 매긴다.

**(e) 커맨드 패널 주석 줄바꿈.** 주석이 칸 폭을 넘으면 옆 칸을 덮는다.
글꼴 폭을 추정해(한글 1.0em / ASCII 0.52em) 직접 접어야 한다. `postprocess_svg.py` 가 한다.

**(f) 역 라벨 부분 채색.** 여러 노선이 각자 다른 DB 를 쓰는데 역을 넷으로 쪼개면 지저분해진다.
`uniprot_euk · _pro · _arc · _virus` 처럼 한 역에 모으고 **접미사만 그 노선 색으로** 칠하면
역 하나로 같은 정보를 준다. 두 노선이 같은 DB 를 쓰면 두 색 그라디언트를 준다.
`scripts/postprocess_svg.py` 의 `colorize` 규칙이 이것이다.

## 5. 0.7.2에 실제로 있는 것

**디렉티브** — `title:` `style:` `line:` `line_order:` `legend:` `legend_min_height:`
`file:` `files:` `dir:` `grid:` `logo:` `entry:` `exit:` `direction:` `compact_offsets:`
`center_ports:` `off_track:`

- `entry:`/`exit:`/`direction:` 은 **subgraph 안에서만** 먹는다 (현재 섹션에 붙는다).
  `exit: bottom | l1,l2` 처럼 `<side> | <노선들>`. side 는 left/right/top/bottom.
- `grid: <section> | col,row[,rowspan[,colspan]]`
- `file: <station> | <배지글자> [| <캡션>]` — 캡션은 역 라벨과 겹치기 쉬우니 짧게 쓰거나 생략한다.
- 노선 스타일은 `solid` `dashed` `dotted`.

**서브커맨드** — `render` `validate` `info` `convert`

**render 플래그** — `-o` `--format svg|html` `--theme nfcore|light` `--width` `--height`
`--x-spacing` `--y-spacing` `--max-layers-per-row` `--animate/--no-animate` `--debug`
`--logo` `--line-order definition|span` `--straight-diamonds/--no-straight-diamonds`
`--center-ports/--no-center-ports` `--section-x-gap` `--section-y-gap` `--from-nextflow` `--title`

`--format html` 은 pan/zoom + 노선별 필터가 붙은 단일 HTML 을 낸다.

## 6. 노선을 무엇으로 잡을 것인가

노선 축을 잘못 잡으면 지도가 읽히지 않는다. **하나를 고르면 나머지가 따라 정해지는 것**을 축으로 삼는다.

| 파이프라인 | 좋은 축 | 왜 |
|---|---|---|
| T1_Reseq | mapper × quantifier 조합 | 사용자가 실제로 고르는 것이 그 조합이다 |
| T2_Denovo | **종 정보(kingdom)** | 종이 정해지면 lineage · DB · KofamScan 유무가 함께 정해진다 |

도구 이름을 축으로 잡으면 안 된다. Trimmomatic / TrimGalore 처럼 **같은 자리의 택일**은
노선이 아니라 한 역의 대안이다.

같은 노선 안의 실행 차이(트림 도구 택일 등)는 **색을 바꾸지 말고** 같은 색으로
갈렸다 합류시킨다. 색이 바뀌면 다른 갈래가 시작된 것처럼 보인다.

**"하거나 안 하거나" 는 역 하나를 두고 그 역을 지나치는 우회로를 그린다.**
`merge 안 함` 같은 역을 따로 만들면 하지 않는 일에 이름을 붙이게 되고 역만 늘어난다.

**nf-metro 로는 이 그림이 안 나온다.** 세 가지를 다 해 봤다.

| 시도 | 결과 |
|---|---|
| 같은 노선에 `A→M→B` 와 `A→B` 를 함께 건다 | 한 노선은 한 경로만 지난다. 한쪽만 그려지고 우회로는 사라진다 |
| 양쪽에 역을 두어 다이아몬드로 만든다 | 그려지긴 하지만 **합류점이 본선 아래로 내려가** 뒤 구간 전체가 한 칸 처진다 |
| `off_track:` 로 역을 띄운다 | 부풀긴 하는데 항상 위로만 가고, 역시 뒤 구간이 처진다 |

그래서 **직선으로 렌더한 뒤 우회로만 얹는다** — `postprocess_svg.py --bypass 역id:라벨[:반폭:높이]`.
그 역을 가로지르는 수평 선분에서 노선별 레일 y 를 읽어 같은 간격으로 위로 부풀린 곡선을
노선 색마다 하나씩 그리고, 역 글리프는 만들지 않는다. 역 라벨은 아래로 내려 자리를 비운다.
본선은 손대지 않으므로 뒤 구간이 처지지 않는다.

## 6-1. 한 영역 안에서 하위 묶음은 음영으로

영역을 쪼개면 우회 차선이 생기고(§6-2), 그렇다고 다 합치면 무엇이 무엇인지 안 보인다.
**상자는 하나로 두고 안에서 옅은 음영으로만 묶는다** — `postprocess_svg.py --group 라벨:역id,...`.

묶음 이름은 음영 **안쪽 왼쪽 가장자리에 세로로** 세운다. 역 이름은 역 위에 가로로 놓이므로
가로로 쓰면 반드시 겹친다. 음영은 노선보다 뒤에, 이름은 노선보다 앞에 그린다 —
같은 자리에 넣으면 이름이 레일에 덮인다.

역이 하나뿐인 묶음은 세로 이름이 음영보다 길어진다. 이름 길이만큼 음영 높이를 늘리고,
`--y-spacing` 을 넉넉히(90~110) 줘서 옆 묶음과 붙지 않게 한다.

## 6-1b. 공이 안 지나는 갈래

`--animate` 는 노선마다 몇 개의 경로에만 공을 붙인다. 분기가 많으면 **한 번도 공이 지나지 않는
갈래**가 생긴다. 내가 직접 그린 우회로도 마찬가지다(nf-metro 가 모르는 경로다).

**조각만 이어 붙이면 안 된다.** 그 구간만 잘라 공을 태우면 그 자리에서 공이 갑자기
생겨난 것처럼 보인다. 갈림길에서 갈라져 나온 것처럼 보이려면 **출발점부터 이어진 전체 경로**를
만들어야 한다. `build_route()` 가 그 노선의 선분들로 그래프를 만들고 시작점 → 대상 역 → 끝점
경로를 BFS 로 찾아 d 를 이어 붙인다.

**우회 호는 nf-metro 갈래와 같은 비례로 그려야 한다.** 자기가 그린 갈래만 모양이 다르면
같은 도면 안에서 바로 티가 난다. nf-metro 는 `짧은 직진(8) → 가파른 사선(가로 26 · 세로 전체)
→ 긴 평행 → 사선 → 직진` 으로, 꺾이는 점마다 반지름 10 의 2차 곡선을 넣는다.
사선의 가로 폭을 키우거나 반폭을 좁히면 사선이 모서리 곡선에 먹혀 **뭉개진 덩어리**가 된다.
깊이도 옆 갈래와 비슷하게 준다 (`--bypass 역:라벨:반폭:깊이[:down]`).

`--animate-through 역id` 가 그 일을 한다. `--bypass` 도 자기가 그린 호를 그 전체 경로 가운데에
갈아 끼운 뒤 공을 태운다. 어느 역이 비었는지는 motion path 좌표를 역 좌표와 대조해 확인한다.

## 6-2. 영역을 쪼개면 우회 차선이 생긴다

한 역(예: Unigene)에서 여러 갈래가 병렬로 뻗어 나갈 때, 그 갈래들을 **각각 다른 영역에 나눠 담으면**
앞 영역에 정차하지 않는 노선이 그 영역을 우회하는 차선으로 그려진다. 실제로는 없는 단계가
있는 것처럼 읽힌다.

**서로 순서가 없는 갈래는 한 영역에 묶는다.** 정량·조립 QC·ORF 예측처럼 같은 산출물에서
동시에 갈라지는 것들은 영역 하나에 넣고, 제목에 "순서 없음" 을 적는 편이 낫다.

## 7. 병렬을 순서로 그리지 말 것

BLAST DB 처럼 **서로 독립적으로 도는 것**을 한 줄로 이으면 순서가 있는 것처럼 읽힌다.
같은 앞 역에서 여러 역으로 각각 엣지를 내면 nf-metro 가 세로로 나란히 배치한다.

종류가 열 개를 넘어가면 한 줄에 두지 말고 **그 영역만 아래 행으로 접어** 세로로 길게 편다
(`%%metro grid:` 로 row 를 하나 내린다). 한눈에 "이건 목록이지 순서가 아니다" 로 읽힌다.

한 역에 **어느 노선이 서는지**는 엣지의 노선 목록이 정한다. 서지 않는 노선을 빼면
그 노선은 그 역을 통과한 것으로 그려진다 — Virus 가 BUSCO 를 건너뛰는 표현이 이것이다.

## 함정

- **한글**: `.mmd`는 UTF-8 저장 + `PYTHONUTF8=1`.
- 노선 색은 배경 대비를 위해 진한 색으로. 노란색은 light 테마에서 가늘게 보인다.
- 역 id는 소문자+언더스코어, 라벨은 대괄호 안에: `star_rsem[RSEM]`.
- 역 라벨에 괄호는 써도 되지만 `[...]` 안에 `]` 를 넣으면 파싱이 깨진다.
- 노선이 6~7개를 넘으면 범례와 역이 두꺼워져 읽기 힘들다 — 축을 다시 잡거나 지도를 나눈다.
- 같은 HTML 문서에 지도를 둘 이상 인라인으로 넣으면 **id가 충돌해 두 번째 지도의 애니메이션이
  첫 번째 경로를 따라간다.** 지도마다 `id=` `href="#..."` `url(#...)` 에 접두사를 붙인다.
