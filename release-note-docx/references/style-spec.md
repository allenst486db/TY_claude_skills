# 스타일 스펙

`assets/lib.js`가 구현하는 시각 규격의 근거. 두 원본 Word 문서의 `word/document.xml`을
직접 언집해 색상 hex·폰트·크기(half-point)를 추출했다.

- **전체 개요(F 팔레트)** 출처: `GSEA_가이드_Release_Note.docx` (앞선 버전)
- **버전 상세(P 팔레트)** 출처: `DemultiConfirm_릴리스노트.docx`

두 팔레트를 하나의 문서 안에서 그대로 함께 쓴다(개요는 F, 버전 블록은 P) — 억지로
통일하지 않는다. 사용자가 "이 부분은 이 문서 양식처럼" 이라고 부분별로 지정했을 때는
이렇게 원본 그대로 결합하는 것이 맞다.

## 색상

### F 팔레트 (개요)
| 토큰 | hex | 용도 |
|---|---|---|
| `F.navy` | `1F3864` | 큰 제목 |
| `F.accent` | `2E5395` | eyebrow 텍스트, 요약 표 기본 배지색 |
| `F.grey` | `595959` | 메타 라인, 표 날짜 열 |
| `F.lightGrey` | `F2F2F2` | (예비) |
| `F.line` | `D9D9D9` | 메타 라인 구분자 |

### P 팔레트 (버전 상세)
| 토큰 | hex | 용도 |
|---|---|---|
| `P.primary` | `1B1F8C` | 소제목, 표 헤더 배경, 기본 태그색, appendix 제목 |
| `P.navy` | `00216B` | 버전 번호(큰 Consolas), 부서명, 인라인 코드칩 텍스트 |
| `P.gray` | `6B7280` | 날짜, "—" 연결자, 헤더/푸터 텍스트 |
| `P.grayDark` | `374151` | 레벨1 하위 불릿 텍스트 |
| `P.codeBg` | `F2F2F7` | 인라인 코드칩 배경 |
| `P.divider` | `D9D9D9` | 버전 사이 구분선 |
| `P.danger` | `C0392B` | "버그 수정" 계열 라벨/태그 |
| `P.success` | `1E7A46` | "확인" 라벨 |
| `P.warning` | `B7791F` | "영향받던 증상" 등 주의 라벨 |
| `P.black` | `111827` | 비교표의 "이전" 값 등 중립 텍스트 |

`TAG_COLORS` 매핑: `bug`/`fix`/`breaking` → danger, `feature`/`improve`/`docs` →
primary, `chore` → gray. `resolveColor()`가 6자리 hex를 직접 받으면 매핑을 거치지
않고 그대로 사용한다.

## 폰트 · 크기 (half-point 단위. pt = 값/2)

| 요소 | 폰트 | 크기 | 굵기 | 색 |
|---|---|---|---|---|
| eyebrow "RELEASE NOTE" | Consolas | 18 (9pt) | bold | F.accent |
| 개요 큰 제목 | 맑은 고딕 | 40 (20pt) | bold | F.navy |
| 메타 라인 | 맑은 고딕 | 20 (10pt) | — | F.grey |
| "Release Note"/"개요" 헤딩 | 맑은 고딕 | 24 (12pt) | bold | F.navy |
| 개요 본문 | 맑은 고딕 | 21 (10.5pt) | — | `262626` |
| 요약 표 헤더 | 맑은 고딕 | 20 (10pt) | bold | 흰색 (배경 F.navy) |
| 요약 표 버전 배지 | Consolas | 19 (9.5pt) | bold | 흰색 (배경 카테고리색) |
| 요약 표 날짜 | Consolas | 19 (9.5pt) | — | F.grey |
| 요약 표 수정 항목 | 맑은 고딕 | 19 (9.5pt) | bold | categoryColor |
| 요약 표 요약 | 맑은 고딕 | 19 (9.5pt) | — | `262626` |
| 버전 번호(큰 헤더) | Consolas | 34 (17pt) | bold | P.navy |
| 버전 헤더의 날짜 | 맑은 고딕 | 22 (11pt) | — | P.gray |
| 버전 헤더의 대괄호 태그 | 맑은 고딕 | 20 (10pt) | bold | tagColor |
| 변경 항목 소제목 | 맑은 고딕 | 21 (10.5pt) | bold | P.primary |
| 본문 문단 | 맑은 고딕 | 20 (10pt) | — | 기본(검정) |
| 인라인 코드칩 | Consolas | 19 (9.5pt) | — | P.navy, 배경 P.codeBg |
| 레벨0 불릿 라벨 | 맑은 고딕 | 20 (10pt) | bold | labelColor |
| 레벨0 불릿 "—" | 맑은 고딕 | 20 (10pt) | — | P.gray |
| 레벨1 하위 불릿 | 맑은 고딕 | 19 (9.5pt) | — | P.grayDark |
| 비교표 헤더 | 맑은 고딕 | 19 (9.5pt) | bold | 흰색 (배경 P.primary) |
| 비교표 셀 | 맑은 고딕/Consolas | 18 (9pt) | 선택 | P.black 또는 bold 시 P.navy |
| appendix 제목 | 맑은 고딕 | 30 (15pt) | bold | P.primary |
| 각주 | 맑은 고딕 | 17 (8.5pt) | italic | P.gray |
| 헤더/푸터 | 맑은 고딕 | 16 (8pt) | — | P.gray |

## 구조

```
[헤더: 우측 정렬, "<제목> Release Note"]

RELEASE NOTE                         ← eyebrow
<제목>                                ← 큰 제목
문서: <docName>   |   갱신일: <date>   ← 메타
Release Note                          ← heading (요청에 따라 문구 교체 가능)
<개요 문단>
┌────┬──────┬──────────┬────────┐
│버전│날짜  │수정 항목  │요약    │     ← 요약 표, 최신이 첫 행
└────┴──────┴──────────┴────────┘

─────────────────────────────────    ← divider

v1.2   2026-09-02   [내용 오류 수정]  ← 버전 헤더 (최신부터)
  <변경 항목 소제목>
  <본문 문단(들)>
  ● <라벨> — <설명>
  ● <설명>
  ┌──────┬──────┐
  │수정전│수정후│
  └──────┴──────┘
  <다음 변경 항목...>

─────────────────────────────────    ← divider

v1.1   ...

─────────────────────────────────    ← divider (footnoteText가 있을 때만)
<각주, italic>

[푸터: 중앙, "<부서명>  ·  <페이지번호>"]
```

## 불릿 numbering

`numId=1`(reference `"rn-bullets"`)에 두 레벨만 정의:
- level 0: `●`, indent left 720 twip, hanging 360
- level 1: `○`, indent left 1440 twip, hanging 360

원본 DemultiConfirm 문서는 level 2 이상(`■` 등)도 numbering.xml에 정의돼 있었지만
실제 문서 본문에서는 사용되지 않았다 — 필요해지면 `numberingConfig()`에 레벨을
추가한다.

## 페이지 설정

A4 (`11906 × 16838` DXA), 여백 1440 DXA(1인치) 사방 동일. 헤더/푸터 거리는
Word 기본값(708 DXA)을 그대로 쓴다 — `lib.js`는 별도로 지정하지 않는다.
