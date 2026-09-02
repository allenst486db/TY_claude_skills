---
name: release-note-docx
description: >-
  버전별 갱신 이력을 담은 Word(.docx) 릴리스 노트를 작성하는 형식. 사용자가
  "릴리스 노트", "release note", "버전별 갱신 내역", "changelog word 문서",
  "이전 버전과 지금 버전 변경 이력" 등을 요청하며 결과물이 .docx일 때 사용한다.
  전체 개요(제목·메타·요약 표)는 파랑/네이비 팔레트의 심플한 형식, 버전별 상세는
  큰 버전 번호 + 날짜 + 대괄호 수정 항목 태그 + 색상 라벨 불릿 + 비교표로 구성된
  형식을 결합해 재사용한다. docx(npm) 기반 assets/lib.js를 그대로 require해서 쓴다.
---

# 릴리스 노트 (release-note-docx)

두 문서에서 뽑아낸 형식을 결합한 Word 릴리스 노트 빌더.

- **전체 개요(맨 위 front matter)** — `RELEASE NOTE` eyebrow, 큰 제목, 메타 라인
  (`문서: … | 갱신일: …`), `Release Note` 제목의 개요 문단, **버전 / 날짜 / 수정 항목 /
  요약** 4열 요약 표. 파랑/네이비(F 팔레트) 톤.
- **버전별 상세(본문)** — `v1.2   2026-09-02   [내용 오류 수정]` 같은 큰 버전 헤더,
  볼드 인디고 소제목, `**라벨** — 설명` 형태의 색상 구분 불릿, 수정 전/후 비교표,
  버전 사이 얇은 구분선. 인디고/네이비(P 팔레트) 톤.
- **항상 최신 버전이 맨 위**로 오도록 정렬한다 (요약 표·본문 모두).
- 헤더(우측 상단)에 문서 제목, 푸터(중앙)에 부서명 · 페이지 번호가 자동으로 들어간다.

## 언제 쓰는가

- "릴리스 노트 작성해줘", "버전별 갱신 내역 word로", "changelog 문서 만들어줘" 등
- 스크립트/도구/가이드 문서가 여러 차례 수정되었고, 그 변경 이력을 격식 있는
  Word 문서로 정리해 배포해야 할 때
- 이미 이 형식으로 만든 릴리스 노트가 있고, 새 버전 항목을 추가해야 할 때

## 사용법

1. `require('docx')`가 되는지 확인한다. 안 되면 `npm install docx` (docx-js 공통
   주의사항은 `docx` 스킬의 gotcha 목록을 따른다: A4 기본 크기, ImageRun에 `type`
   필수, 테이블은 `columnWidths`+각 셀 `width` 이중 지정 등 — 이 스킬에서는
   테이블 관련 주의사항만 해당).
2. `assets/lib.js`를 프로젝트로 복사(또는 그대로 require)한다.
3. `assets/generate.example.js`를 복사해 실제 값(제목/버전/날짜/변경 내용)을
   채운 뒤 실행한다 — `node generate.js`.
4. 결과를 반드시 렌더링해서 확인한다 (docx 스킬의 검증 절차와 동일):
   ```
   python scripts/office/soffice.py --headless --convert-to pdf output.docx
   pdftoppm -jpeg -r 100 output.pdf page
   ```
   LibreOffice/`soffice`가 없는 Windows 환경(이 스킬이 만들어진 환경 포함)에서는
   Microsoft Word가 설치돼 있다면 PowerShell + Word COM으로 대체한다:
   ```powershell
   $word = New-Object -ComObject Word.Application
   $word.Visible = $false
   $doc = $word.Documents.Open("<절대경로>\output.docx", $false, $true)
   $doc.SaveAs([ref]"<절대경로>\output.pdf", [ref]17)  # wdFormatPDF
   $doc.Close(); $word.Quit()
   ```
   그 뒤 Read 도구로 PDF를 직접 열어 텍스트/레이아웃을 확인한다(포이지 이미지가
   함께 반환된다).

## 핵심 API (`assets/lib.js`)

`RN.buildDocument(opts)` 하나만 호출하면 전체 문서가 완성된다.

```js
const RN = require("./lib.js");
const { run, code, b, P } = RN;

const doc = RN.buildDocument({
  headerText: "제품명 Release Note",      // 페이지 우측 상단
  footerDept: "부서명",                    // 페이지 하단 중앙 (· 페이지번호 자동 추가)
  frontMatter: {
    title: "제품명",
    docName: "문서/배포물 경로",
    updatedDate: "YYYY-MM-DD",
    heading: "Release Note",              // "개요" 대신 이 문구를 쓰고 싶으면 그대로 둔다
    overview: "개요 문단.",
    summaryHeaders: ["버전", "날짜", "수정 항목", "요약"],
    summaryRows: [                        // 최신 버전이 배열 첫 원소
      { version: "v1.1", versionColor: P.danger, date: "YYYY-MM-DD",
        category: "[버그 수정]", categoryColor: P.danger, summary: "한 줄 요약" },
    ],
  },
  versions: [                             // 최신 버전이 배열 첫 원소
    {
      version: "v1.1", date: "YYYY-MM-DD", tag: "[버그 수정]", tagColor: "bug",
      sections: [
        {
          heading: "변경 항목 제목",
          paragraphs: [ [run("설명 문장 안에 "), code("inline.code"), run("를 섞는다.")] ],
          bullets: [
            { label: "수정 내용", labelColor: "bug", text: "..." },
            { text: "라벨 없는 일반 불릿" },
            { text: "하위 불릿", level: 1 },
          ],
          table: { headers: ["수정 전", "수정 후"], rows: [[{text:"..."}, {text:"...", bold:true}]] },
        },
      ],
    },
  ],
  footnoteText: "문서 맨 아래 각주(선택).",
});

RN.Packer.toBuffer(doc).then((buf) => require("fs").writeFileSync("output.docx", buf));
```

`tagColor` / `labelColor`는 `"bug"|"feature"|"fix"|"breaking"|"docs"|"improve"|"chore"`
같은 의미 키워드나, 6자리 hex(`"C0392B"` 등)를 그대로 받는다. 색상 의미는
`references/style-spec.md`에 전체 목록이 있다.

## 자주 하는 실수

- `versions`/`summaryRows` 배열을 오래된 순서로 넣기 → **항상 최신이 첫 원소**.
- `heading` 필드를 안 넘겨서 기본값 "Release Note"가 나오는데, 사용자가 원한 문구가
  다를 수 있음 → 요청받은 정확한 문구를 `heading`에 넣는다.
- 표 안에 코드/파일명을 넣을 때 `code: true`를 안 줘서 일반 텍스트로 보임 →
  `compareTable` cellSpec에 `code: true` 지정.
- 버전 태그·요약 표의 "수정 항목" 색을 서로 다르게 둠 → 같은 버전이면 같은 색으로
  통일해야 한 눈에 매칭된다(`categoryColor`를 버전 블록의 `tagColor`와 동일하게).
- 결과를 렌더링해서 눈으로 확인하지 않고 바로 전달 → 표 줄바꿈, 하이픈 단어
  줄바꿈 등은 텍스트만 봐서는 못 잡는다. 반드시 PDF로 변환해 확인한다.

## 레퍼런스

- `assets/lib.js` — 전체 빌더 함수 (require해서 바로 사용)
- `assets/generate.example.js` — 최소 사용 예시 (복사해서 값만 채우면 됨)
- `references/style-spec.md` — 색상 팔레트·폰트·크기·구조를 두 원본 문서에서
  추출한 상세 스펙. 새로운 컴포넌트를 추가하거나 스타일을 손볼 때 참고.
