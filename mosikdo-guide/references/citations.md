# 출처 표기 레퍼런스

근거가 있는 문서(기술 검토, 리서치 보고, 서비스 제안)에서 **출처를 문장 옆에
바로 보이게** 다는 규약. 각주 번호 방식을 쓰지 않는 이유부터 마크업까지.

## 왜 각주 번호를 쓰지 않는가

`<sup>[1]</sup>` 방식은 읽는 사람이 **문서 끝까지 내려가야 근거를 알 수 있다**.
화면으로 읽는 문서에서는 그 왕복이 일어나지 않고, 결국 근거가 없는 것과 같아진다.
게다가 번호는 항목을 추가·삭제할 때마다 전부 어긋난다 — 본문 `[4]`와 목록
4번이 다른 자료를 가리키는 사고가 실제로 잘 난다.

그래서 이 시스템은 **이름표(칩)** 를 쓴다. 문장 끝에서 `Nature 2026`,
`bioRxiv Mathur`, `사내 T1_Reseq`처럼 **자료의 정체가 바로 읽히고**, 누르면 해당
항목으로 이동한다. 번호가 없으니 순서를 바꿔도 깨지지 않는다.

## 색이 근거 등급이다

이 시스템의 다른 색 규약과 마찬가지로, 출처 칩의 색도 장식이 아니다.
**독자가 "이 문장을 얼마나 믿어도 되는지"를 색으로 먼저 안다.**

| 클래스 | 색 | 의미 | 예시 라벨 |
|---|---|---|---|
| `.src` | 파랑 | 검증된 1차 자료 (peer-reviewed 논문, 공식 규격) | `Nature 2026` |
| `.src.pre` | 주황 | **미검증·잠정** (preprint, 벤더 블로그, 2차 요약) | `bioRxiv Mathur` |
| `.src.doc` | 회색 | 공식 문서·저장소 (GitHub, API docs, 모델카드) | `NVIDIA NIM` |
| `.src.local` | 보라 | 내부 자료 (사내 소스, 사내 문서) | `사내 T1_Reseq` |

> 주황을 아끼지 말 것. preprint를 파랑으로 달면 문서 전체의 신뢰도가 깎인다.
> 등급을 낮춰 다는 쪽이 항상 안전하다.

## 마크업

### 본문 — 인라인 칩

문장 **끝**(마침표 앞)에 붙인다. 라벨은 짧게, 자료가 식별되게.

```html
<p>9조 염기쌍을 학습했다<a class="src" href="#ref-nature26">Nature 2026</a>.</p>

<li>단거리 신호에 blind spot이 있다<a class="src pre" href="#ref-mathur">bioRxiv Mathur</a></li>

<li>엔드포인트가 제공된다<a class="src doc" href="#ref-nim">NVIDIA NIM</a></li>
```

여러 자료가 한 문장을 뒷받침하면 칩을 **나란히** 붙인다. 공백 없이 이어 쓴다
(칩 자체가 `margin-left`를 갖는다).

```html
<p>라이선스는 Apache-2.0이다<a class="src" href="#ref-nature26">Nature 2026</a><a class="src doc" href="#ref-gh">GitHub evo2</a>.</p>
```

### 출처 섹션 — 목록

마지막 섹션으로 둔다. `<ol>`이 아니라 **`<ul class="refs">`** 를 쓴다(번호 없음).
각 항목은 `id`와 `.ref-tag`를 갖고, **태그 라벨은 본문 칩 라벨과 글자까지 같아야 한다.**

```html
<p class="ref-h">원논문 (peer-reviewed)</p>
<ul class="refs">
  <li id="ref-nature26"><span class="ref-tag">Nature 2026</span><br><strong>Brixi G, et al. "제목." <em>Nature</em> 652(8112):1349–1361 (2026-03-04).</strong>
    <span class="meta">DOI: <a href="https://doi.org/10.1038/...">10.1038/...</a> · PMID 41781614</span>
    <span class="meta">인용 — 이 자료에서 실제로 가져온 내용. → 본문 어느 항목의 근거인지</span>
  </li>
</ul>
```

`id`는 `ref-` 접두사 + 짧은 슬러그(`ref-nature26`, `ref-mathur`, `ref-t1reseq`).
`.refs li`에 `scroll-margin-top:80px`이 들어 있어 sticky 타이틀바에 가려지지
않고, `:target`이면 왼쪽에 강조 테두리가 생겨 어디로 왔는지 보인다.

### 등급 범례

출처 섹션 앞에 한 번 넣어 색 규약을 알린다.

```html
<div class="src-legend">
  <span style="color:var(--accent-ink);background:var(--accent-soft)">파랑 · 검증된 1차 자료</span>
  <span style="color:var(--orange);background:var(--orange-soft)">주황 · 미검증/잠정</span>
  <span style="color:var(--ink-2);background:var(--panel)">회색 · 공식 문서</span>
  <span style="color:var(--purple);background:var(--panel)">보라 · 내부 자료</span>
</div>
```

문서 앞부분(리드 아래 `.note.info`)에도 한 줄로 알려 주면 독자가 칩을 처음
만났을 때 헤매지 않는다.

## 각 항목에 반드시 넣는 것

1. **`.ref-tag`** — 본문 칩과 동일한 라벨
2. **서지 정보** — 저자, 제목, 저널/사이트, 날짜(가능하면 일자까지)
3. **식별자·링크** — DOI, PMID, URL. 내부 자료는 **파일 경로**
4. **`인용 —`** 줄 — *이 자료에서 실제로 무엇을 가져왔는지*. 이게 핵심이다.
   나중에 검증할 때 원문 어디를 봐야 하는지 알려 준다.
5. **`→` 역매핑** — 본문의 어느 항목(섹션·서비스·주장)의 근거인지

웹 자료는 문서 상단이나 출처 섹션 첫 문단에 **접근일**을 한 번 밝힌다.

## 정직하게 표기하기

- **2차 요약에만 근거한 내용**은 본문에 `<span style="color:var(--orange)">※ 원문
  확인 필요</span>`를 남기고, 문서 끝 `.note.warn`에 "확인 필요 항목"으로 모은다.
- **직접 도출한 제안**(원문에 없는 아이디어)은 출처를 달지 말고 **제안임을
  명시**한다. 근거 있는 것처럼 칩을 붙이면 안 된다.
- **preprint를 인용했으면** 항목 끝과 문서 footer 양쪽에 `peer review 미완료`를
  적는다.
- 내부 자료는 **실제로 열어 본 파일만** 적는다. 경로와 확인한 내용을 함께.

## 자주 하는 실수

- 각주 번호(`<sup>[1]</sup>`)로 되돌아가기 → 유지보수에서 반드시 어긋난다.
- 칩 라벨과 `.ref-tag` 라벨이 다름 → 독자가 연결을 못 한다. **글자까지 같게.**
- 문단 전체에 칩 하나만 달기 → 어느 문장의 근거인지 모른다. **문장 단위로.**
- preprint·블로그를 파랑으로 → 등급 인플레이션. 문서 전체 신뢰도가 깎인다.
- `인용 —` 줄 생략 → 목록이 링크 모음으로 전락한다. 나중에 검증이 불가능해진다.
- 칩을 문장 중간에 넣기 → 읽기 흐름이 끊긴다. 문장 끝, 마침표 앞.
