# nf-metro reference (v1.1)

공식 문서: https://seqeralabs.github.io/nf-metro/dev/ · 플레이그라운드에서 브라우저로 미리보기 가능.

## 디렉티브

| Directive | Scope | 설명 |
|---|---|---|
| `%%metro title: <text>` | Global | 제목 (좌상단) |
| `%%metro logo: <path>` | Global | 제목 대신 PNG 로고 |
| `%%metro style: <dark\|light>` | Global | 테마 |
| `%%metro line: <id> \| <name> \| <color> [\| <style>]` | Global | 노선 정의. style: `solid`(기본), `dashed`, `dotted` |
| `%%metro grid: <section> \| <col>,<row>[,<rowspan>[,<colspan>]]` | Global | 섹션 배치 고정 |
| `%%metro legend: <pos>` | Global | `tl` `tr` `bl` `br` `bottom` `right` `none` (`\| canvas`, `\| dx,dy`, `x,y` 가능) |
| `%%metro line_order: <definition\|span>` | Global | 노선 정렬 |
| `%%metro file: <station> \| <label> [\| <name>] [\| banner]` | Global | 문서 아이콘 종점 |
| `%%metro files: <station> \| <label>` | Global | 문서 여러 장 아이콘 (paired) |
| `%%metro dir: <station> \| <label>` | Global | 폴더 아이콘 |
| `%%metro off_track: <station>[, ...]` | Global | 본선 위로 띄워 배치 |
| `%%metro process: <station> \| <regex>` | Global | Nextflow 프로세스 매핑 (live progress) |
| `%%metro compact_offsets: true` | Global | 역 크기를 실제 통과 노선 수에 맞춤 |
| `%%metro center_ports: true` | Global | 섹션 간 포트 중앙 정렬 |
| `%%metro line_spread: <bundle\|centered\|rails>[ \| <section>...]` | Global/Section | 한 역을 지나는 노선의 세로 관계 |
| `%%metro animate: true` | Global | 흐르는 점 애니메이션 |
| `%%metro directional: true` | Global | 방향 셰브론 |
| `%%metro manifest: false` | Global | 임베디드 JSON manifest 생략 |
| `%%metro entry: <side> \| <lines>` | Section | 진입 포트 방향 (`left/right/top/bottom`) |
| `%%metro exit: <side> \| <lines>` | Section | 진출 포트 방향 |
| `%%metro direction: <LR\|RL\|TB>` | Section | 섹션 내 흐름 방향 |

## CLI

```
nf-metro render|validate|info|convert|serve|validate-svg|check-mapping
```
(설치가 PATH에 없으면 `python -m nf_metro ...`)

`render` 주요 옵션 — 모두 디렉티브로도 지정 가능하며 플래그가 우선한다.

| 옵션 | 기본 | 설명 |
|---|---|---|
| `-o, --output PATH` | `<input>.svg` | 출력 |
| `--format svg\|html` | `svg` | html은 pan/zoom·노선 isolate 되는 self-contained 페이지 |
| `--theme nfcore\|light\|seqera` | `nfcore` | 테마 |
| `--animate` / `--directional` | off | 점 애니메이션 / 방향 셰브론 |
| `--line-spread bundle\|centered\|rails` | `bundle` | 겹침 해소 1순위 |
| `--x-spacing / --y-spacing FLOAT` | auto | 간격 |
| `--fold-threshold INT` | 15 | 한 줄 최대 역 열 수 (넘으면 다음 행으로 접힘) |
| `--section-x-gap / --section-y-gap` | 50 | 섹션 간격 |
| `--width / --height INT` | auto | 캔버스 (하단 패널 여백 확보용) |
| `--font-scale FLOAT` | 1.0 | 텍스트 + 간격 스케일 |
| `--label-angle FLOAT` | theme | 역 라벨 각도 |
| `--compact-offsets` | off | 역 두께 최소화 |
| `--legend TEXT` | auto | 범례 위치 |
| `--line-order definition\|span` | definition | 노선 순서 |
| `--diamond-style straight\|symmetric` | straight | fork-join 배치 |
| `--responsive` | off | width/height 없이 viewBox만 (웹 임베드) |
| `--embed-font` | off | Inter를 base64로 인라인 |
| `--bare` | off | 제목·여백 제거 |
| `--no-dark-mode-css` | off | 다크모드 CSS 블록 제거 (호스트가 테마 관리할 때) |
| `--no-chrome-css` | off | `var()` 대신 실색상 (cairosvg 래스터화용) |
| `--from-nextflow` | off | Nextflow `-with-dag` mermaid 입력을 변환 후 렌더 |
| `--strict` | off | 레이아웃 불변식 위반을 에러로 |
| `--debug` | off | 포트/웨이포인트 디버그 오버레이 |
| `--validate` | off | 렌더된 geometry 검사 |

`validate --with-layout` : 레이아웃 엔진까지 돌려 검사.
`validate-svg <svg> --geometry` : 선이 역 라벨/마커를 관통하는지, 서로 다른 노선이 한 선으로 겹쳤는지.
`explain` : 레이아웃 결정 이유 출력 (배치가 이상할 때).
`convert <dag.mmd>` : Nextflow DAG → `.mmd` 초안.

## 기존 파이프라인에서 뽑아내기

Nextflow면 `nextflow run ... -preview -with-dag dag.mmd` → `nf-metro convert dag.mmd -o map.mmd` 후 손질.
그 외(파이썬 오케스트레이터 등)는 실행 스크립트에서 단계·도구·조합 제약을 읽어 직접 `.mmd`를 쓴다.
