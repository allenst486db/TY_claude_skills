# 모식도(SVG) 패턴 레퍼런스

인라인 SVG로 개념을 그리는 규약과 복붙 스니펫. 목표는 **일관된 룩**과 **테마 대응**이다.

## 공통 규약

- **감싸기**: 항상 `figure > .fig-scroll > svg.dg` 구조. 넓은 그림은 모바일에서
  가로 스크롤된다. 위에 `<p class="scroll-hint">← 좌우 스크롤</p>`, 아래
  `<figcaption>결론 한 줄</figcaption>`.
- **좌표**: `viewBox="0 0 700 H"`를 기준으로 그린다(폭 700이 `.content` 폭에 잘 맞음).
  높이 H는 내용에 맞춰. `width:100%`는 CSS가 처리.
- **색**: 반드시 `fill="var(--...)"` / `stroke="var(--...)"`. 그래야 다크모드가 따라온다.
  예외: 컬러 노드 안의 글자 `fill="#fff"`는 의도적이라 OK.
- **화살표**: 문서 상단 숨김 defs의 `#ah` 하나만 재사용. 실선은 `class="ar"`,
  점선(생략/매핑)은 `class="ar-d"` 또는 직접 `stroke-dasharray="4 4"`.
- **텍스트 클래스**: `.ttl`(노드 제목 12.5px 굵게) · `.lbl`(라벨 11px) · `.cap`(캡션 9.5px).
  더 크게 강조할 땐 인라인 `font-size`/`font-weight`.
- **노드**: 둥근 사각형 `rx="11~13"`. 기본 `class="nd"`(회색), 핵심/기준
  `class="nd-a"`(파랑 테두리), 결과 성공은 `fill="var(--green-soft)"`.

## 의미 색 매핑 (반드시 준수)

- 파랑(`--accent`) = 신규 조립/처리/기준 생성
- 파랑 solid 노드 = 최종 기준(좌표계)
- 점선 + `--ink-3` = 생략/미참여
- 초록(`--green`) = 가능/성공, 주황(`--orange`) = 주의/부분, 빨강(`--red`) = 불가/실패
- 서로 다른 대상 구분 = `--purple` `--cyan` `--pink` (의미색과 겹치지 않게)

---

## 패턴 1 — 선형 흐름 (A → B → C)

가장 기본. 노드 사이를 `.ar`로 잇는다.

```html
<figure>
  <div class="fig-scroll">
    <svg class="dg" viewBox="0 0 700 160" role="img" aria-label="흐름">
      <rect x="24" y="56" width="120" height="48" rx="12" class="nd"/>
      <text x="84" y="84" class="ttl" text-anchor="middle">입력</text>
      <line x1="148" y1="80" x2="196" y2="80" class="ar"/>
      <rect x="200" y="56" width="120" height="48" rx="12" class="nd-a"/>
      <text x="260" y="78" class="ttl" fill="var(--accent-ink)" text-anchor="middle">처리</text>
      <text x="260" y="94" class="cap" text-anchor="middle">핵심 단계</text>
      <line x1="324" y1="80" x2="372" y2="80" class="ar"/>
      <rect x="376" y="56" width="140" height="48" rx="12" fill="var(--green-soft)" stroke="none"/>
      <text x="446" y="84" class="ttl" fill="var(--green)" text-anchor="middle">✓ 결과</text>
    </svg>
  </div>
</figure>
```

## 패턴 2 — 수렴 (여러 입력 → 하나로)

"모든 샘플이 한 번에 조립된다" 류. 각 입력에서 처리 노드로 `.ar`를 모은다.

```html
<svg class="dg" viewBox="0 0 700 190" role="img" aria-label="수렴">
  <rect x="20" y="34" width="150" height="132" rx="12" fill="var(--accent-soft)" stroke="none"/>
  <rect x="34" y="46" width="122" height="20" rx="10" fill="var(--accent)"/>
  <text x="95" y="60" font-size="10" fill="#fff" text-anchor="middle" font-weight="600">샘플 1</text>
  <rect x="34" y="72" width="122" height="20" rx="10" fill="var(--accent)" opacity=".75"/>
  <text x="95" y="86" font-size="10" fill="#fff" text-anchor="middle" font-weight="600">샘플 2</text>
  <rect x="34" y="98" width="122" height="20" rx="10" fill="var(--accent)" opacity=".55"/>
  <text x="95" y="112" font-size="10" fill="#fff" text-anchor="middle" font-weight="600">샘플 N</text>
  <line x1="174" y1="100" x2="216" y2="100" class="ar"/>
  <rect x="220" y="76" width="98" height="48" rx="12" class="nd-a"/>
  <text x="269" y="97" class="ttl" fill="var(--accent-ink)" text-anchor="middle">Assembly</text>
  <text x="269" y="113" class="cap" text-anchor="middle">1회 · 통합</text>
  <line x1="322" y1="100" x2="364" y2="100" class="ar"/>
  <!-- 기준 서열(패턴 5의 색막대)로 이어감 -->
</svg>
```

일부만 참여시키는 변형: 참여 샘플은 채운 색, 미참여 샘플은
`fill="var(--card)" stroke="var(--line)"`로 비우고, 미참여→기준으로 `class="ar-d"`
곡선(`<path d="M.. C ..">`)을 그려 "매핑만"을 표현.

## 패턴 3 — 발산 → 불가 (여러 결과가 안 합쳐짐)

"샘플마다 기준이 달라 비교 불가" 류. 여러 결과에서 금지 기호로 점선을 모은다.
금지 기호는 아래 [패턴 6] 참고.

```html
<!-- 각 파이프라인 결과에서 -->
<line x1="430" y1="50"  x2="558" y2="118" stroke="var(--ink-3)" stroke-width="1.4" stroke-dasharray="4 4"/>
<line x1="430" y1="146" x2="558" y2="140" stroke="var(--ink-3)" stroke-width="1.4" stroke-dasharray="4 4"/>
<line x1="430" y1="242" x2="558" y2="162" stroke="var(--ink-3)" stroke-width="1.4" stroke-dasharray="4 4"/>
<!-- + 금지 기호(패턴 6) + "불가" 라벨 -->
```

## 패턴 4 — 의사결정 트리

조건 노드 → 예/아니오 분기. 분기는 `<path>`로 꺾고, 라벨은 `.cap`.

```html
<svg class="dg" viewBox="0 0 700 260" role="img" aria-label="결정 트리">
  <rect x="230" y="14" width="240" height="46" rx="12" class="nd"/>
  <text x="350" y="42" class="ttl" text-anchor="middle">조건 질문?</text>
  <line x1="470" y1="37" x2="520" y2="37" class="ar"/>
  <text x="505" y="28" class="cap" text-anchor="middle">예</text>
  <rect x="524" y="14" width="150" height="46" rx="12" class="nd" stroke-dasharray="4 4"/>
  <text x="599" y="42" class="lbl" text-anchor="middle" fill="var(--ink-3)">분기 A</text>
  <line x1="350" y1="60" x2="350" y2="94" class="ar"/>
  <text x="374" y="82" class="cap">아니오</text>
  <rect x="270" y="98" width="160" height="42" rx="12" fill="var(--accent-soft)" stroke="none"/>
  <text x="350" y="124" class="ttl" fill="var(--accent-ink)" text-anchor="middle">분기 B</text>
  <!-- 좌우로 더 나눌 땐 <path d="M270,119 L130,119 L130,158" class="ar"/> 식으로 꺾기 -->
</svg>
```

## 패턴 5 — "Contig set = 색막대" 은유

De novo 특유의 "기준 서열"을 길이·색이 다른 막대 묶음으로 표현. 서로 다른
set은 색 팔레트를 바꿔 "다름"을 한눈에 보이게 한다.

```html
<!-- set A: 파랑 계열 -->
<text x="360" y="44" class="lbl">Contig set A</text>
<rect x="360" y="52" width="72"  height="11" rx="5.5" fill="var(--accent)"/>
<rect x="360" y="68" width="108" height="11" rx="5.5" fill="var(--cyan)"/>
<rect x="360" y="84" width="54"  height="11" rx="5.5" fill="var(--green)"/>

<!-- set B: 보라/주황/핑크 계열 = 확연히 다른 set -->
<text x="360" y="192" class="lbl">Contig set B</text>
<rect x="360" y="200" width="98" height="11" rx="5.5" fill="var(--purple)"/>
<rect x="360" y="216" width="60" height="11" rx="5.5" fill="var(--orange)"/>
<rect x="360" y="232" width="86" height="11" rx="5.5" fill="var(--pink)"/>
```

누락되는 서열은 빈 점선 막대: `<rect … fill="none" stroke="var(--orange)" stroke-dasharray="4 3"/>`.

## 패턴 6 — 금지 기호 (불가)

원 + 45° 회전한 빨간 바. "병합 불가 / 비교 불가"에 쓴다.

```html
<circle cx="608" cy="151" r="30" fill="none" stroke="var(--red)" stroke-width="3"/>
<rect x="590" y="146" width="36" height="10" rx="5" fill="var(--red)" transform="rotate(-45 608 151)"/>
<text x="608" y="205" font-size="13" font-weight="700" fill="var(--red)" text-anchor="middle">병합 불가</text>
<text x="608" y="223" class="cap" text-anchor="middle">기준이 다름</text>
```

## 패턴 7 — 나란한 비교 패널 (된다 vs 안 된다, 좋다 vs 나쁘다)

두 개의 큰 배경 패널(`--green-soft` vs `--orange-soft`, 또는 `--panel` 2개)을
좌우로 두고, 안에 막대·수치로 대비. 품질/편차 비교, 예시 대조에 강력하다.

```html
<svg class="dg" viewBox="0 0 700 220" role="img" aria-label="비교">
  <rect x="16" y="20" width="326" height="184" rx="14" fill="var(--green-soft)" stroke="none"/>
  <text x="36" y="48" class="ttl" fill="var(--green)">좋은 경우</text>
  <text x="36" y="66" class="cap">조건 설명</text>
  <!-- 안에 막대: 배경 트랙 fill="var(--card)" + 값 막대 fill="var(--green)" -->
  <rect x="110" y="92" width="216" height="12" rx="6" fill="var(--card)"/>
  <rect x="110" y="92" width="150" height="12" rx="6" fill="var(--green)"/>
  <text x="36" y="188" font-size="11" font-weight="700" fill="var(--green)">결론</text>

  <rect x="358" y="20" width="326" height="184" rx="14" fill="var(--orange-soft)" stroke="none"/>
  <text x="378" y="48" class="ttl" fill="var(--orange)">나쁜 경우</text>
  <!-- 대칭으로 orange 값 막대 … -->
  <text x="378" y="188" font-size="11" font-weight="700" fill="var(--orange)">결론</text>
</svg>
```

---

## 크기·간격 감각

- 노드 높이 44~52, 좌우 폭 88~150. 노드 간 화살표 길이 40~48.
- 텍스트가 노드보다 커지지 않게. 9.5px 미만은 피한다(모바일 가독성).
- 한 그림에 요소가 많아 700 폭을 넘기면 높이를 늘려 세로로 쌓거나, 그림을 둘로 나눈다.
- 항상 마지막에 `figcaption`으로 "이 그림의 결론"을 한 문장 적는다 — 그림만 보고도
  요점이 남게.
