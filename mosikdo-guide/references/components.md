# 컴포넌트 마크업 레퍼런스

`assets/template.html`의 CSS가 정의하는 컴포넌트들. 필요한 것만 복사해 쓴다.
색·간격은 CSS가 처리하니 마크업만 맞추면 된다.

## 목차
- [섹션 헤더](#섹션-헤더)
- [콜아웃 (note)](#콜아웃-note)
- [조건 카드 (cards)](#조건-카드-cards)
- [방식 블록 (method)](#방식-블록-method)
- [불릿 리스트 (pts)](#불릿-리스트-pts)
- [예시 (ex)](#예시-ex)
- [비교표 (table)](#비교표-table)
- [체크리스트 (check)](#체크리스트-check)
- [코드블록 / 터미널 (termwin)](#코드블록--터미널-termwin)
- [출처 표기 (src / refs)](#출처-표기-src--refs)

---

## 섹션 헤더

번호 칩 + mono 키커 + 제목. 섹션마다 번호를 1씩 올린다.

```html
<section>
  <div class="sec-head"><span class="sec-num">2</span><p class="kicker">Decision</p></div>
  <h2>분석 방향 결정 흐름</h2>
  <p>본문…</p>
</section>
```

인라인 강조는 `<span class="hl">…</span>`(강조색), `<code>…</code>`(파일명/명령),
`<strong>`(굵게).

---

## 콜아웃 (note)

5가지 톤. 의미에 맞게 고른다.

| 클래스 | 색 | 쓰임 |
|---|---|---|
| `.note.info` | 파랑 | 용어 정리, 참고 |
| `.note.ok` | 초록 | 추천 상황, 가능 조건 |
| `.note.warn` | 주황 | 주의, 부분적 한계 |
| `.note.danger` | 빨강 | 반드시 확인, 불가 조건 |
| `.note.plain` | 회색 | 중립 보조 설명 |

```html
<div class="note danger">
  <span class="lbl">핵심 원칙</span>
  <p>함께 분석할 대상은 반드시 <strong>동일 기준으로 처리</strong>되어야 한다.</p>
  <p style="margin-top:.5rem">두 번째 문단은 이렇게.</p>
</div>
```

---

## 조건 카드 (cards)

"이럴 때 이 카테고리" 같은 짧은 조건 3~4개를 나란히.

```html
<div class="cards">
  <div class="cd"><div class="t">최초 진행</div><div class="d">기존 결과가 없는 경우</div></div>
  <div class="cd"><div class="t">본사 default</div><div class="d">표준·권장 방식</div></div>
  <div class="cd"><div class="t">Reference 부재</div><div class="d">필수 파일 누락</div></div>
</div>
```

---

## 방식 블록 (method)

여러 "방식/옵션"을 각각 카드로 설명할 때의 기본 단위. 배지 + 제목 + 결과 pill(들)
+ 설명 + (모식도) + 특성 리스트 + 콜아웃 순.

```html
<div class="method">
  <div class="m-head">
    <span class="m-badge">A-1</span>            <!-- .alt 붙이면 회색(비주류 방식) -->
    <h3>Assembly group = 모든 샘플</h3>
    <span class="m-pill ok">전체 DEG 가능</span>  <!-- ok / warn / no -->
  </div>
  <p class="m-desc">한 줄 요약 설명.</p>

  <!-- 여기에 <div class="fig-scroll"><svg class="dg">…</svg></div> 모식도 -->

  <p class="sub-h">특성</p>
  <ul class="pts">
    <li>일반 특성</li>
    <li class="warn"><strong>주의</strong> — 한계나 위험</li>
  </ul>

  <div class="note ok" style="margin-top:1.1rem">
    <span class="lbl">추천 상황</span>
    <p>언제 이 방식을 고르는지.</p>
  </div>
</div>
```

결과 pill은 여러 개 붙일 수 있다: `<span class="m-pill ok">가능</span>
<span class="m-pill warn">일부 누락</span>`.

---

## 불릿 리스트 (pts)

컬러 점이 의미를 나른다. 기본(파랑)·`.warn`(주황)·`.no`(빨강).

```html
<ul class="pts">
  <li>기본 항목</li>
  <li class="warn"><strong>전제 조건</strong> — 이게 있어야 함</li>
  <li class="no"><strong>불가</strong> — 이건 안 됨</li>
</ul>
```

작은 mono 소제목이 필요하면 리스트 앞에 `<p class="sub-h">특성</p>`.

---

## 예시 (ex)

번호 뱃지 + 설명. 잘못된/함정 예시는 `.bad`(빨강 번호).

```html
<p class="sub-h">적용 예시</p>
<div class="ex"><span class="n">예시 1</span><div>정상 사례 설명. <strong>강조</strong>.</div></div>
<div class="ex bad"><span class="n">예시 3</span><div>함정 사례 — <strong>이렇게 하면 비교 불가</strong>.</div></div>
```

---

## 비교표 (table)

`.table-wrap`로 감싸 모바일 가로 스크롤. 헤더에 `.sub`로 mono 부제. 셀 값은
`.yes`(초록)·`.no-c`(빨강)·`.par`(주황)로 의미 표시.

```html
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>구분</th>
        <th>A-1<span class="sub">전체</span></th>
        <th>A-3<span class="sub">개별</span></th>
      </tr>
    </thead>
    <tbody>
      <tr><th>샘플 간 DEG</th><td class="yes">가능</td><td class="no-c">불가</td></tr>
      <tr><th>분석 시간</th><td>가장 김</td><td>중간</td></tr>
    </tbody>
  </table>
</div>
```

---

## 체크리스트 (check)

"요청/진행 전 확인 사항". 체크박스 + 굵은 리드 + 설명.

```html
<div class="check">
  <div class="ck"><span class="box">✓</span><div><strong>대상을 모두 확정했는가</strong> — 이유·결과.</div></div>
  <div class="ck"><span class="box">✓</span><div><strong>전제 파일이 있는가</strong> — 이유.</div></div>
</div>
```

---

## 코드블록 / 터미널 (termwin)

여러 줄 명령·코드는 macOS 터미널 창처럼 보여준다. `.termwin`(창) > `.termbar`
(트래픽 라이트 + 가운데 타이틀) > `pre.term`(본문) 구조. 타이틀에는 맥락을 넣으면
좋다(작업 이름이나 작업 경로, 예: `~/.claude/skills — Terminal`).

`pre.term` 안에서 인라인 `<span>`으로 의미를 색으로 구분한다:
`.c`=주석(회색), `.k`=명령/키워드(파랑), `.p`=프롬프트/강조(초록). HTML이므로
`<`, `&`는 `&lt;`, `&amp;`로 이스케이프한다. 들여쓰기·줄바꿈은 `pre`가 그대로 살린다.

```html
<div class="termwin">
  <div class="termbar"><span class="dots"></span><span class="tt">~/.claude/skills — Terminal</span></div>
  <pre class="term"><span class="c"># 주석</span>
<span class="k">git pull</span>
<span class="k">git add</span> -A &amp;&amp; <span class="k">git commit</span> -m "update: &lt;내용&gt;"
<span class="k">git push</span></pre>
</div>
```

> 한 줄짜리 명령이나 파일명·플래그는 이 무거운 블록 대신 인라인 `<code>…</code>`를 쓴다.

---

## 출처 표기 (src / refs)

근거가 있는 문장 **끝**에 이름표 칩을 붙이고, 마지막 섹션에 출처 목록을 둔다.
각주 번호는 쓰지 않는다. 칩 색이 근거 등급을 나른다.

```html
<!-- 본문: 문장 끝, 마침표 앞 -->
<p>9조 염기쌍을 학습했다<a class="src" href="#ref-nature26">Nature 2026</a>.</p>
<li>blind spot이 있다<a class="src pre" href="#ref-mathur">bioRxiv Mathur</a></li>

<!-- 출처 섹션: <ol>이 아니라 <ul class="refs">. 태그 라벨은 본문 칩과 동일하게 -->
<ul class="refs">
  <li id="ref-nature26"><span class="ref-tag">Nature 2026</span><br><strong>저자. "제목." <em>저널</em> (날짜).</strong>
    <span class="meta">DOI: <a href="https://doi.org/...">10.xxxx/...</a></span>
    <span class="meta">인용 — 이 자료에서 실제로 가져온 내용. → 본문 어느 항목의 근거인지</span>
  </li>
</ul>
```

| 클래스 | 색 | 의미 |
|---|---|---|
| `.src` / `.ref-tag` | 파랑 | 검증된 1차 자료 |
| `.src.pre` / `.ref-tag.pre` | 주황 | 미검증 (preprint·블로그·2차 요약) |
| `.src.doc` / `.ref-tag.doc` | 회색 | 공식 문서·저장소 |
| `.src.local` / `.ref-tag.local` | 보라 | 내부 자료 |

범례(`.src-legend`), 앵커 연결 규칙, 정직하게 표기하는 법은
**`references/citations.md`** 에 전부 정리돼 있다.
