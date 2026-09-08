# nf-metro 레퍼런스 — 0.7.2 (PyPI 실제 판)

`pip install nf-metro` 로 받으면 **0.7.2** 가 온다. 이 문서는 그 판을 소스에서 확인해 정리한 것이다.

> **주의 — 이 리포의 이전 판 문서는 "2.0" 기준이었는데, 그런 배포판은 PyPI 에 없다.**
> 거기 적혀 있던 `mode:` `legend_combo:` `line_spread:` `group:` `interchange:` `marker:`
> `marker_legend:` `caption:` `process:` `auto_process:` `animate:` `fold_threshold:` 등의
> 디렉티브와 `validate-svg` 서브커맨드, `--line-spread` `--fold-threshold` `--inactive-lines`
> `--mode` `--no-chrome-css` 플래그는 **0.7.2 에 없다.** 쓰면 조용히 무시되거나 에러가 난다.
> 공식 문서 https://seqeralabs.github.io/nf-metro/dev/ 는 배포되지 않은 개발판을 설명하고 있으므로,
> **문서보다 `nf-metro render --help` 를 믿을 것.**

## 서브커맨드

```
nf-metro render   <file.mmd>   # SVG 또는 HTML 로 렌더
nf-metro validate <file.mmd>   # 스펙 오류 검사
nf-metro info     <file.mmd>   # 섹션/노선/역 요약
nf-metro convert  <dag.mmd>    # Nextflow -with-dag 결과를 .mmd 로 변환
```

## render 플래그 (전량)

| 플래그 | 기본값 | 설명 |
|---|---|---|
| `-o, --output PATH` | `<input>.<format>` | 출력 경로 |
| `--format [svg\|html]` | `svg` | `html` 은 pan/zoom + 노선별 필터가 붙은 단일 페이지 |
| `--theme [nfcore\|light]` | `nfcore` | **테마는 이 플래그로만 바뀐다** (아래 함정 참조) |
| `--width INTEGER` | 자동 | SVG 폭 |
| `--height INTEGER` | 자동 | SVG 높이. 아래에 패널을 붙일 여백 확보용 |
| `--x-spacing FLOAT` | 60 | 레이어 간 가로 간격 |
| `--y-spacing FLOAT` | 자동 | 트랙 간 세로 간격. 라벨이 붙으면 자동으로 벌어진다 |
| `--max-layers-per-row INTEGER` | 15 | 이 값을 넘으면 다음 행으로 접는다 |
| `--animate / --no-animate` | off | 노선 위를 흐르는 원 |
| `--debug / --no-debug` | off | 포트·숨은 역·엣지 웨이포인트 표시 |
| `--logo PATH` | — | `%%metro logo:` 를 덮어씀 |
| `--line-order [definition\|span]` | `definition` | `.mmd` 선언 순 / 구간 길이 순 |
| `--straight-diamonds / --no-` | on | 분기-합류에서 위쪽 갈래를 본선에 유지 |
| `--center-ports / --no-` | 디렉티브 따름 | 섹션 간 포트를 짧은 쪽 중앙에 맞춤 |
| `--section-x-gap FLOAT` | 50 | 섹션 간 가로 간격 |
| `--section-y-gap FLOAT` | 40 | 섹션 간 세로 간격 |
| `--from-nextflow` | off | 입력을 `-with-dag` 결과로 보고 먼저 변환 |
| `--title TEXT` | — | `--from-nextflow` 와 함께 쓰는 제목 |

## 디렉티브 (0.7.2 파서가 실제로 읽는 것 전부)

`%%metro <key>: <payload>` 형식. 알 수 없는 key 는 **조용히 무시**된다 (경고도 없다).

### 전역 — `graph LR` 위에 쓴다

| 디렉티브 | 설명 |
|---|---|
| `title: <text>` | 좌상단 제목 |
| `logo: <path>` | 제목 대신 이미지 |
| `line: <id> \| <범례 텍스트> \| <#색상> [\| solid\|dashed\|dotted]` | 노선 정의. 3필드 필수 |
| `line_order: <definition\|span>` | 노선 정렬 |
| `legend: <tl\|tr\|bl\|br\|bottom\|right\|none>` | 범례 위치 |
| `legend_min_height: <float>` | 범례 영역 최소 높이 |
| `file: <station> \| <배지글자> [\| <캡션>]` | 문서 아이콘 종점 |
| `files: <station> \| <배지글자> [\| <캡션>]` | 문서 여러 장 |
| `dir: <station> \| <배지글자> [\| <캡션>]` | 폴더 |
| `grid: <section> \| <col>,<row>[,<rowspan>[,<colspan>]]` | 섹션 배치 고정 |
| `off_track: <station>[, ...]` | 본선에서 띄워 배치 |
| `compact_offsets: <true\|false>` | 트랙 오프셋을 좁힘 |
| `center_ports: <true\|false>` | 섹션 간 포트를 중앙 정렬 |
| `style: <name>` | **읽기는 하지만 렌더에 쓰이지 않는다.** `info` 출력에만 나온다 |

### 섹션 안 — `subgraph ... end` 블록 안에 쓴다

| 디렉티브 | 설명 |
|---|---|
| `entry: <left\|right\|top\|bottom> \| <line1,line2,...>` | 그 섹션으로 들어오는 위치 힌트 |
| `exit: <left\|right\|top\|bottom> \| <line1,line2,...>` | 나가는 위치 힌트 |
| `direction: <LR\|RL\|TB>` | 섹션 내부 흐름 방향 |

밖에 쓰면 `current_section_id` 가 없어 **무시된다.** 이 셋은 반드시 subgraph 안이다.

## 역(station) 모양

라벨 문법이 모양을 정한다.

```
id[라벨]      네모   (기본)
id([라벨])    스타디움
id[[라벨]]    서브루틴
id((라벨))    원
id(라벨)      둥근 네모
id{라벨}      마름모
id            라벨 없이 id 그대로
```

`[...]` 안에 `]` 를 넣으면 파싱이 깨진다. 괄호는 괜찮다.

## 함정 (0.7.2 에서 실제로 겪은 것)

1. **테마는 `--theme` 로만 바뀐다.** `%%metro style: light` 는 파싱은 되지만
   렌더러가 `graph.style` 을 읽지 않는다. `--theme light` 를 반드시 붙인다.
2. **애니메이션 디렉티브는 없다.** `%%metro animate: true` 는 무시된다. `--animate` 를 쓴다.
3. **움직이는 원은 흰색 고정이다.** 노선 색을 입히려면 후처리한다 —
   `<circle r="3.0" ...>` 안의 `<mpath href="#motion-path-<lineid>-<n>"/>` 에서 노선 id 를 읽어
   `fill` 을 그 노선 색으로 바꾼다. 속도는 `dur="<초>s"` 를 나눈다.
4. **영역 배지 번호는 흐름 순서가 아니다.** `(연결성분, sweep, grid_col, grid_row)` 순으로 매겨져,
   아래 행으로 접은 섹션이 위 행 섹션보다 앞 번호를 받는다. 보는 사람은 그것을 단계 순서로
   읽으므로, `data-section-id` 를 보고 후처리로 다시 매긴다.
5. **하단 커맨드 패널 기능은 없다.** `</svg>` 앞에 `<rect>`+`<text>` 를 직접 넣고
   `width/height/viewBox` 를 늘린다. `scripts/postprocess_svg.py` 가 3·4·5 를 한 번에 한다.
6. **같은 HTML 문서에 지도를 둘 이상 인라인하면 id 가 충돌한다.**
   두 번째 지도의 `<mpath href="#motion-path-...">` 가 첫 지도의 경로를 잡아 애니메이션이 엉킨다.
   지도마다 `id=` `href="#..."` `url(#...)` 에 접두사를 붙인다.
7. **고정폭 글꼴에서 한글은 두 칸.** 커맨드 패널에서 공백으로 열을 맞추면 어긋난다.
   라벨 겹침을 기계로 검사할 때도 폭은 한글 1.0em / ASCII 0.58em 으로 잡아야 맞는다.
8. **`file:` 캡션은 역 라벨과 겹치기 쉽다.** 아이콘 옆 역의 라벨과 같은 자리에 오므로,
   캡션을 생략하거나 역 라벨을 캡션과 다른 말로 바꾼다.
