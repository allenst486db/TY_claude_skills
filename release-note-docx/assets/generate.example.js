/**
 * release-note-docx / generate.example.js
 * lib.js 사용 예시 — 실제로는 이 파일을 복사해 값만 바꿔 쓴다.
 */
const fs = require("fs");
const path = require("path");
const RN = require("./lib.js");
const { run, code, b, P } = RN;

const doc = RN.buildDocument({
  headerText: "제품명 Release Note",
  footerDept: "부서명",
  frontMatter: {
    title: "제품명",
    docName: "문서 파일명 또는 배포물 경로",
    updatedDate: "YYYY-MM-DD",
    heading: "Release Note",
    overview: "이 제품/문서의 버전별 변경 이력이다. 최신 버전이 위에 오도록 정리했다.",
    summaryHeaders: ["버전", "날짜", "수정 항목", "요약"],
    summaryRows: [
      { version: "v1.1", versionColor: P.danger, date: "YYYY-MM-DD", category: "[버그 수정]", categoryColor: P.danger, summary: "한 줄 요약" },
      { version: "v1.0", versionColor: P.primary, date: "YYYY-MM-DD", category: "[최초 배포]", categoryColor: P.primary, summary: "한 줄 요약" },
    ],
  },
  // 최신 버전을 배열의 첫 원소로.
  versions: [
    {
      version: "v1.1", date: "YYYY-MM-DD", tag: "[버그 수정]", tagColor: "bug",
      sections: [
        {
          heading: "수정한 문제의 제목",
          paragraphs: [
            [run("일반 설명 문장 안에 "), code("inline.code"), run(" 를 섞어 쓸 수 있다.")],
          ],
          bullets: [
            { label: "수정 내용", labelColor: "bug", text: "무엇을 어떻게 고쳤는지" },
            { label: "확인", labelColor: "success", text: "어떻게 검증했는지" },
            { text: "라벨 없는 일반 불릿" },
            { text: "들여쓴 하위 불릿", level: 1 },
          ],
          table: {
            headers: ["수정 전", "수정 후"],
            rows: [[
              { text: "이전 동작 설명" },
              { text: "이후 동작 설명", bold: true },
            ]],
          },
        },
      ],
    },
  ],
  footnoteText: "이 문서에 대한 각주.",
});

RN.Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(path.join(__dirname, "example-output.docx"), buf);
  console.log("done");
});
