---
name: metro-map
description: 파이프라인/워크플로우를 nf-core 스타일 지하철 노선도(metro map) SVG로 그린다. 사용자가 "metro map", "메트로맵", "노선도", "flow diagram", "파이프라인 다이어그램", "nf-core 스타일 다이어그램"을 요청하거나, 여러 도구 조합(mapper × quantifier 등)이 각각 하나의 색 노선으로 표현되는 분석 워크플로우를 그림으로 정리하려 할 때 사용한다. 옵션 모듈이 점선으로 갈라지고 구간(섹션)별로 묶이는 다단계 파이프라인 도식에 적합하다. 단순 박스-화살표 순서도나 개념 모식도는 svg-infographic / mosikdo-guide 를 쓴다.
---

# Metro map (nf-metro)

노선도는 손으로 SVG를 쓰지 않는다. `nf-metro`가 Mermaid 유사 `.mmd` → SVG 레이아웃을 전부 계산한다.
당신이 할 일은 **`.mmd` 스펙을 정확히 쓰는 것**뿐이다.

## 0. 설치 확인

```bash
python -m nf_metro --version || pip install nf-metro
```

Windows + 한글 라벨이면 **반드시** `PYTHONUTF8=1`을 붙인다 (없으면 cp949 UnicodeDecodeError):

```bash
PYTHONUTF8=1 python -m nf_metro render map.mmd -o map.svg
```

## 1. 먼저 사실을 모은다 (그리기 전)

`.mmd`를 쓰기 전에 아래를 확정한다. 모르면 코드/설정을 읽거나 사용자에게 묻는다 — 추측해서 그리면 틀린 노선도가 나온다.

1. **구간(section)** — Pre-processing / Alignment / Quantification / Optional / Report 같은 단계 묶음
2. **노선(line)** — 사용자가 고를 수 있는 **조합 하나 = 노선 하나**. 예: `HISAT2+StringTie(기본)`, `STAR+RSEM`, `TopHat+Cufflinks`. 금지 조합은 노선에서 뺀다.
3. **역(station)** — 각 도구 이름. 한 역을 여러 노선이 지나면 굵기가 자동으로 커진다.
4. **기본값** — 어떤 노선이 default 인지 (범례에 `(default)` 표기)
5. **옵션 모듈** — novel / variant call / fusion 처럼 기본 off 인 경로 → `dashed` 회색 노선 하나로 묶는다
6. **입출력 파일** — 시작 FASTQ, 끝 XLSX/HTML 등 → `%%metro file:`

## 2. `.mmd` 작성

`examples/t1reseq_demo.mmd`를 복사해서 고치는 게 가장 빠르다. 구조:

```
%%metro title: T1_Reseq
%%metro style: light                  # light | dark
%%metro animate: true                 # 노선 위를 흐르는 점
%%metro line: <id> | <범례 텍스트> | <#색상> [| dashed]
%%metro file: <station_id> | FASTQ    # 문서 아이콘 종점
%%metro legend: bl                    # tl tr bl br bottom right none

graph LR
    subgraph pre [Pre-processing]
        %%metro exit: right | line_a, line_b
        fastq[FASTQ]
        trim[Trimmomatic]
        fastq -->|line_a,line_b| trim
    end
    subgraph align [Genome alignment]
        ...
    end
    trim -->|line_a| hisat        # 섹션 간 엣지는 subgraph 밖에
```

핵심 규칙:

- 엣지의 `|...|`에는 **그 구간을 지나는 모든 노선 id**를 콤마로 적는다. 빠뜨리면 노선이 끊긴다.
- 섹션 간 엣지는 모든 `subgraph ... end` **바깥**에 쓴다. 포트/분기역은 자동 생성된다.
- 배치는 자동(topological). 마음에 안 들 때만 `%%metro grid: <section> | col,row[,rowspan[,colspan]]`로 고정한다.
- 색은 참조 팔레트를 재사용: `#2db572`(기본) `#0570b0` `#f5c542` `#ff8c00` `#e63946` `#7b2d3b`, 옵션 점선 `#9e9e9e`.

전체 디렉티브·CLI 옵션 표는 [references/nf-metro.md](references/nf-metro.md).

## 3. 검증 → 렌더

```bash
PYTHONUTF8=1 python -m nf_metro validate map.mmd            # 스펙 오류
PYTHONUTF8=1 python -m nf_metro info map.mmd                # 섹션/노선/역 요약으로 사실 대조
PYTHONUTF8=1 python -m nf_metro render map.mmd -o map.svg --animate
PYTHONUTF8=1 python -m nf_metro validate-svg map.svg --geometry   # 라벨 위로 선이 지나가는지
```

렌더 후 **반드시 눈으로 확인한다** (브라우저 pane 또는 SendUserFile). 확인 포인트: 노선이 끊기지 않았는지, 라벨 겹침, 섹션 배치.

레이아웃이 어긋나면 이 순서로 조정: `--line-spread centered|rails` → `--x-spacing/--y-spacing` → `--fold-threshold` → 마지막에 `%%metro grid:` 수동 고정.

## 4. 선택: 하단 명령어 패널

참조 도면처럼 "Example commands" 블록을 붙이려면, 렌더된 SVG의 `</svg>` 앞에 직접 `<rect>`+`<text>`를 추가한다 (nf-metro 기능 아님). 캔버스가 모자라면 `--height`로 여백을 먼저 확보한다. 폰트는 본문 `'Helvetica Neue', Helvetica, Arial, sans-serif`, 명령어는 `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace` 9.5px.

## 함정

- **한글**: `.mmd`는 UTF-8로 저장 + `PYTHONUTF8=1`. SVG 텍스트는 Inter 폰트라 한글은 시스템 폰트로 폴백된다 — 한글 비중이 크면 렌더 후 `font-family`를 `'Malgun Gothic'` 등으로 치환한다.
- 노선 색은 배경 대비를 위해 진한 색으로. 노란색은 light 테마에서 잘 안 보인다.
- 역 id는 소문자+언더스코어, 라벨은 대괄호 안에: `star_rsem[RSEM]`.
- 노선이 6개를 넘으면 범례와 역이 두꺼워져 읽기 힘들다 — 조합을 묶거나 지도를 나눈다.
