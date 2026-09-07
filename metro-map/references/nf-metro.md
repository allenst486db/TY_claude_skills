# nf-metro reference (v2.0)

공식 문서: https://seqeralabs.github.io/nf-metro/dev/ · 플레이그라운드에서 브라우저로 미리보기 가능.

설치: `pip install nf-metro` (이 문서는 **2.0.0** 기준). PATH에 `nf-metro`가 없으면 `python -m nf_metro ...`.

## 디렉티브

`%%metro <key>: <payload>` 형식. 알 수 없는 key는 경고 후 무시된다.

**핵심(2.0)**: 아래 CLI 레이아웃 옵션은 **전부 같은 이름의 디렉티브로도 쓸 수 있다** (`--fold-threshold 20` ≡ `%%metro fold_threshold: 20`). 플래그가 디렉티브를 이긴다.

`x_spacing` `y_spacing` `section_x_gap` `section_y_gap` `track_gap` `fold_threshold` `diamond_style` `line_order` `row_align` `center_ports` `compact_offsets` `label_angle` `font_scale` `stroke_scale` `logo_scale` `legend_min_height` `legend_logo_gap` `width` `height` `animate` `directional` `strict` `permissive` `auto_process` `process_scope` `manifest` `caption`

### 전역 디렉티브

| Directive | 설명 |
|---|---|
| `%%metro title: <text>` | 제목 (좌상단) |
| `%%metro logo: <path>` | 제목 대신 PNG 로고 |
| `%%metro style: <name>` | 브랜드 테마: `nfcore`(기본) `light` `dark` `nfcore-light` `nfcore-dark` `seqera` `seqera-light` `seqera-dark` |
| `%%metro mode: <light\|dark>` | **2.0** 브랜드와 독립인 표시 모드. 팔레트를 굽어 고정 — 라이트/다크 PNG 내보내기용 |
| `%%metro line: <id> \| <name> \| <color> [\| <style>]` | 노선 정의. style: `solid`(기본) `dashed` `dotted` |
| `%%metro legend: <pos>` | `tl` `tr` `bl` `br` `bottom` `right` `none` (`\| canvas`, `\| dx,dy`, 절대 `x,y` 가능) |
| `%%metro legend_combo: <lineA, lineB[, ...]> \| <label>` | **2.0** 여러 노선을 범례 한 줄로 합침 (rails 모드에선 레일도 공유). 최소 2개 |
| `%%metro grid: <section> \| <col>,<row>[,<rowspan>[,<colspan>]]` | 섹션 배치 고정 |
| `%%metro line_order: <definition\|span>` | 노선 정렬 |
| `%%metro line_spread: <bundle\|centered\|rails>[ \| <section>...]` | 한 역을 지나는 노선의 세로 관계 |
| `%%metro file: <station> \| <label> [\| <name>] [\| banner]` | 문서 아이콘 종점 |
| `%%metro files: <station> \| <label>` | 문서 여러 장 아이콘 (paired) |
| `%%metro dir: <station> \| <label>` | 폴더 아이콘 |
| `%%metro off_track: <station>[, ...]` | 본선 위로 띄워 배치 |
| `%%metro group: <label> \| <station1, station2[, ...]> [\| above\|below]` | **2.0** 여러 역을 묶는 주석 캡션 밴드 (기본 `below`). 역을 옮기지는 않음 |
| `%%metro interchange: <node_id> \| <rail-1 lines> \| <rail-2 lines>[ \| ...]` | **2.0** 한 역을 레일별 서브역으로 전개해 환승역 글리프로 렌더. 레일 최소 2개 |
| `%%metro marker: <station> \| <shape>, <fill>` | **2.0** 역 마커 모양/채움. shape: `circle`(기본) `square` `pill` / fill: `solid`(기본) `open` 또는 색상값 |
| `%%metro marker_legend: <shape>, <fill> \| <caption>` | **2.0** 마커 모양의 의미를 범례에 추가 |
| `%%metro caption: <text>` | **2.0** 좌하단 캡션·출처 한 줄 (예: 'Adapted from …') |
| `%%metro process: <station> \| <regex>` | Nextflow 프로세스 매핑 (live progress) |
| `%%metro process_scope: <prefix>` | **2.0** 프로세스 FQN 공통 접두사 (예: `NFCORE_RNASEQ:RNASEQ`) |
| `%%metro auto_process: true` | **2.0** 역 id를 그대로 프로세스 패턴으로 사용 |
| `%%metro compact_offsets: true` | 역 크기를 실제 통과 노선 수에 맞춤 |
| `%%metro center_ports: true` | 섹션 간 포트 중앙 정렬 |
| `%%metro animate: true` | 흐르는 점 애니메이션 |
| `%%metro directional: true` | 방향 셰브론 |
| `%%metro manifest: false` | 임베디드 JSON manifest 생략 (끄면 `validate-svg`·live 기능도 못 씀) |

### 섹션 디렉티브 (`subgraph ... end` 안에)

| Directive | 설명 |
|---|---|
| `%%metro entry: <side> \| <lines>` | 진입 포트 방향 (`left/right/top/bottom`) |
| `%%metro exit: <side> \| <lines>` | 진출 포트 방향 |
| `%%metro direction: <LR\|RL\|TB\|BT>` | 섹션 내 흐름 방향 |
| `%%metro number: <int>` | **2.0** 섹션 번호 배지 강제 지정 |

## CLI

```
nf-metro render|render-many|validate|info|convert|serve|serve-multi|validate-svg|check-mapping|explain|embed-script
```

`render` 주요 옵션 — 대부분 디렉티브로도 지정 가능하며 플래그가 우선한다.

| 옵션 | 기본 | 설명 |
|---|---|---|
| `-o, --output PATH` | `<input>.<format>` | 출력 (입력 1개일 때만) |
| `--format svg\|html` | `svg` | html은 pan/zoom·노선 isolate 되는 self-contained 페이지 |
| `--theme <name>` | `nfcore` | 위 `style:`과 같은 8종 |
| `--mode light\|dark` | 테마 기본 | **2.0** 팔레트 굽기 |
| `--animate` / `--directional` | off | 점 애니메이션 / 방향 셰브론 |
| `--line-spread bundle\|centered\|rails` | `bundle` | 겹침 해소 1순위 |
| `--x-spacing / --y-spacing FLOAT` | auto | 간격 |
| `--section-x-gap / --section-y-gap` | 50 | 섹션 간격 |
| `--track-gap FLOAT` | 1 | **2.0** 번들 내 선 사이 여백 px (0–3). 3 초과는 라우팅 깨짐 |
| `--fold-threshold INT` | 15 | 한 줄 최대 역 열 수 (넘으면 다음 행으로 접힘) |
| `--diamond-style straight\|symmetric` | straight | fork-join 배치 |
| `--line-order definition\|span` | definition | 노선 순서 |
| `--row-align content\|top` | content | **2.0** 같은 행 섹션 박스 상단 정렬 |
| `--center-ports` / `--compact-offsets` | off | 포트 중앙 정렬 / 역 두께 최소화 |
| `--label-angle FLOAT` | theme | 역 라벨 각도 |
| `--font-scale FLOAT` | 1.0 | 텍스트 + 레이아웃 간격 스케일 |
| `--stroke-scale FLOAT` | 1.0 | **2.0** 선 두께·역 크기 스케일 (축소 배치 시 가독성) |
| `--width / --height INT` | auto | 캔버스 (하단 패널 여백 확보용) |
| `--legend TEXT` | auto | 범례 위치 |
| `--logo PATH` / `--title TEXT` | 디렉티브 | **2.0** 로고·제목 덮어쓰기 |
| `--logo-scale / --legend-min-height / --legend-logo-gap` | auto | **2.0** 범례 블록 미세조정 |
| `--inactive-lines <ids>` | — | **2.0** 지정 노선을 회색 비활성으로. 빈 값이면 전부 활성. `.mmd`는 안 건드림 |
| `--responsive` | off | width/height 없이 viewBox만 (웹 임베드) |
| `--embed-font` | off | Inter를 base64로 인라인 |
| `--text-to-paths` | off | **2.0** 텍스트를 패스로 (폰트 의존 제거, 선택 불가). `pip install "nf-metro[font]"` 필요 |
| `--svg-class-prefix TEXT` | — | **2.0** CSS 클래스 접두사 (한 페이지에 여러 지도 넣을 때 충돌 방지) |
| `--bare` | off | 제목·여백 제거 |
| `--no-dark-mode-css` | off | 다크모드 CSS 블록 제거 (호스트가 테마 관리할 때) |
| `--no-self-color-scheme` | off | **2.0** 루트 `<svg>`의 `color-scheme` 제거 → 호스트 페이지 테마를 상속 |
| `--no-chrome-css` | off | `var()` 대신 실색상 (cairosvg 등 래스터화용) |
| `--from-nextflow` | off | Nextflow `-with-dag` mermaid 입력을 변환 후 렌더 |
| `--validate` | off | 렌더된 geometry 검사 |
| `--strict` | off | 레이아웃 불변식 위반을 에러로 |
| `--permissive` | off | **2.0** 가드 실패를 경고로 낮추고 best-effort 렌더 (`--strict`보다 우선) |
| `--debug` | off | 포트/웨이포인트 디버그 오버레이 |
| `--auto-process` / `--process-scope` | off | **2.0** live progress 매핑 자동화 |

기타 명령:

- `validate [--with-layout] [--strict]` : 그래프 의미 검사. `--with-layout`은 레이아웃 엔진까지 돌린다.
- `info [--verbose] [--json]` : 섹션/노선/역 요약. **2.0** `--verbose`는 섹션 의존 그래프·노선별 경로·자동 추론값·합성 포트까지, `--json`은 전체 구조를 기계용으로.
- `validate-svg <svg> [--geometry]` : manifest 스키마 검사. `--geometry`는 선이 라벨/마커를 관통하는지까지. (오프셋 붕괴 검사는 `render --validate`에서만)
- `explain` : 레이아웃 결정 이유 출력 (배치가 이상할 때).
- `convert <dag.mmd>` : Nextflow DAG → `.mmd` 초안.
- `render-many <manifest.json>` : **2.0** `{input, output, ...render 옵션}` 배열을 한 프로세스에서 일괄 렌더 (인터프리터 기동 비용 절약).
- `serve` / `serve-multi` : live progress 뷰. **2.0** `serve-multi`는 여러 파이프라인이 보고하는 상주 서버.
- `embed-script` : **2.0** 임베드용 드라이버 JS 출력.
- `check-mapping` : `%%metro process:` 매핑 점검.

## 기존 파이프라인에서 뽑아내기

Nextflow면 `nextflow run ... -preview -with-dag dag.mmd` → `nf-metro convert dag.mmd -o map.mmd` 후 손질.
그 외(파이썬 오케스트레이터 등)는 실행 스크립트에서 단계·도구·조합 제약을 읽어 직접 `.mmd`를 쓴다.

## 1.1 → 2.0 요약

깨진 것은 없다. 1.1 문서의 디렉티브·플래그는 이름 그대로 전부 살아 있고, 아래가 더해졌다.

- **모드/테마 분리**: `style:`은 브랜드, `mode:`(`--mode`)는 라이트·다크. 테마 이름이 8종으로.
- **주석 레이어**: `group:` `marker:` `marker_legend:` `caption:` — 도구 이름 외의 설명을 지도 안에 넣을 수 있다.
- **환승/범례**: `interchange:`, `legend_combo:`.
- **디렉티브 = CLI 옵션**: 레이아웃 knob 전부가 `.mmd` 안에서도 지정 가능해져, 렌더 명령을 짧게 유지할 수 있다.
- **출력 제어**: `--inactive-lines`(같은 지도의 조합별 변형), `--svg-class-prefix`, `--text-to-paths`, `--no-self-color-scheme`, `--stroke-scale`, `--track-gap`.
- **운영**: `render-many`, `serve-multi`, `embed-script`, `--permissive`, `info --json/--verbose`, 섹션 `number:`.
