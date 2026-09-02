/**
 * release-note-docx / lib.js
 *
 * docx(npm) 기반 Word 릴리스 노트 빌더.
 * - 전체 개요(front matter)는 GSEA_가이드_Release_Note.docx 형식(F 팔레트)
 * - 버전별 상세(version blocks)는 DemultiConfirm_릴리스노트.docx 형식(P 팔레트)
 * 두 형식을 각자의 색상 그대로 유지한 채 한 문서에 결합한다.
 *
 * require('docx')만으로 동작. 사용법은 SKILL.md / assets/generate.example.js 참고.
 */
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, AlignmentType, BorderStyle, LevelFormat,
  Header, Footer, PageNumber,
} = require("docx");

const FONT_KR = "맑은 고딕";
const FONT_CODE = "Consolas";

// ── 버전 상세 블록 팔레트 (DemultiConfirm_릴리스노트.docx에서 추출) ──
const P = {
  primary: "1B1F8C", // 제목/부제/강조 라벨 (인디고)
  navy: "00216B",    // 버전 번호, 부서명, 코드칩 텍스트 (네이비)
  gray: "6B7280",    // 날짜, 보조 설명, "—" 연결자
  grayDark: "374151",// 레벨1 하위 불릿 텍스트
  codeBg: "F2F2F7",  // 인라인 코드칩 배경
  divider: "D9D9D9", // 버전 사이 구분선
  white: "FFFFFF",
  danger: "C0392B",  // [버그 수정] 등
  success: "1E7A46",  // "확인" 라벨
  warning: "B7791F",  // "영향받던 증상" 라벨
  black: "111827",
};

// ── 전체 개요(front matter) 팔레트 (GSEA_가이드_Release_Note.docx에서 추출) ──
const F = {
  navy: "1F3864",
  accent: "2E5395",
  grey: "595959",
  lightGrey: "F2F2F2",
  line: "D9D9D9",
};

// 카테고리(수정 항목) → 색상 매핑. 필요하면 호출부에서 직접 hex를 넘겨도 됨.
const TAG_COLORS = {
  bug: P.danger,
  fix: P.danger,
  breaking: P.danger,
  feature: P.primary,
  improve: P.primary,
  docs: P.primary,
  chore: P.gray,
};

function resolveColor(key, fallback) {
  if (!key) return fallback;
  if (/^[0-9A-Fa-f]{6}$/.test(key)) return key;
  return TAG_COLORS[key] || fallback;
}

// ───────────────────────── 런/세그먼트 헬퍼 ─────────────────────────

/** 일반 텍스트 런 (버전 상세 블록 팔레트 기준, size 단위: half-point) */
function run(text, opts = {}) {
  return new TextRun({ text, font: FONT_KR, size: 20, color: "111111", ...opts });
}

/** 인라인 코드 칩 (Consolas + 옅은 배경) */
function code(text, opts = {}) {
  return new TextRun({
    text, font: FONT_CODE, size: 19, color: P.navy,
    shading: { type: ShadingType.CLEAR, fill: P.codeBg },
    ...opts,
  });
}

/** 볼드 강조 런 */
function b(text, opts = {}) {
  return run(text, { bold: true, ...opts });
}

// ───────────────────────── 구분선 ─────────────────────────

/** 버전 사이 얇은 회색 가로선 (빈 문단 + 하단 border 트릭) */
function divider(paletteColor = P.divider) {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, color: paletteColor, size: 4, space: 1 } },
    spacing: { before: 200, after: 200 },
    children: [new TextRun({ text: "", size: 2 })],
  });
}

// ───────────────────────── 전체 개요 (front matter, F 팔레트) ─────────────────────────

/**
 * 문서 맨 위 개요 블록.
 * @param {object} o
 * @param {string} o.eyebrow      - 상단 라벨 (기본 "RELEASE NOTE")
 * @param {string} o.title        - 문서/제품 제목
 * @param {string} o.docName      - 메타 라인의 "문서: " 뒤에 올 값
 * @param {string} o.updatedDate  - 메타 라인의 "갱신일: " 뒤에 올 값
 * @param {string} o.heading      - 개요 섹션 제목 (기본 "Release Note")
 * @param {string} o.overview     - 개요 본문 문단
 * @param {string[]} o.summaryHeaders - 요약 표 헤더 (예: ["버전","날짜","수정 항목","요약"])
 * @param {Array<{version:string, versionColor?:string, date:string, category:string,
 *                 categoryColor?:string, summary:string}>} o.summaryRows
 *        최신 버전이 배열의 첫 번째 항목이 되도록 정렬해서 넘길 것.
 */
function frontMatter(o) {
  const paras = [];
  paras.push(new Paragraph({
    spacing: { after: 40 },
    children: [new TextRun({ text: o.eyebrow || "RELEASE NOTE", bold: true, size: 18, color: F.accent, font: FONT_CODE })],
  }));
  paras.push(new Paragraph({
    spacing: { after: 60 },
    children: [new TextRun({ text: o.title, bold: true, size: 40, color: F.navy, font: FONT_KR })],
  }));
  paras.push(new Paragraph({
    spacing: { after: 240 },
    children: [
      new TextRun({ text: `문서: ${o.docName}`, size: 20, color: F.grey, font: FONT_KR }),
      new TextRun({ text: "   |   ", size: 20, color: F.line, font: FONT_KR }),
      new TextRun({ text: `갱신일: ${o.updatedDate}`, size: 20, color: F.grey, font: FONT_KR }),
    ],
  }));
  paras.push(new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 320, after: 120 },
    children: [new TextRun({ text: o.heading || "Release Note", bold: true, size: 24, color: F.navy, font: FONT_KR })],
  }));
  paras.push(new Paragraph({
    spacing: { after: 120, line: 300 },
    children: [new TextRun({ text: o.overview, size: 21, color: "262626", font: FONT_KR })],
  }));
  if (o.summaryRows && o.summaryRows.length) {
    paras.push(new Paragraph({ spacing: { before: 100, after: 260 }, children: [] }));
    paras.push(summaryTable(o.summaryHeaders, o.summaryRows));
  }
  return paras;
}

/** 개요 아래 버전 요약 표 (버전 / 날짜 / 수정 항목 / 요약). widths 합계 9800 DXA. */
function summaryTable(headers, rows, widths) {
  const w = widths || [1300, 1700, 2400, 4400];
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) => new TableCell({
      width: { size: w[i], type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: F.navy },
      margins: { top: 100, bottom: 100, left: 140, right: 140 },
      children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: h, bold: true, size: 20, color: "FFFFFF", font: FONT_KR })] })],
    })),
  });
  const bodyRows = rows.map((r) => new TableRow({
    children: [
      new TableCell({
        width: { size: w[0], type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: resolveColor(r.versionColor, F.accent) },
        margins: { top: 100, bottom: 100, left: 140, right: 140 },
        children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: r.version, bold: true, size: 19, color: "FFFFFF", font: FONT_CODE })] })],
      }),
      new TableCell({
        width: { size: w[1], type: WidthType.DXA },
        margins: { top: 100, bottom: 100, left: 140, right: 140 },
        children: [new Paragraph({ children: [new TextRun({ text: r.date, size: 19, color: F.grey, font: FONT_CODE })] })],
      }),
      new TableCell({
        width: { size: w[2], type: WidthType.DXA },
        margins: { top: 100, bottom: 100, left: 140, right: 140 },
        children: [new Paragraph({ children: [new TextRun({ text: r.category, bold: true, size: 19, color: resolveColor(r.categoryColor, F.navy), font: FONT_KR })] })],
      }),
      new TableCell({
        width: { size: w[3], type: WidthType.DXA },
        margins: { top: 100, bottom: 100, left: 140, right: 140 },
        children: [new Paragraph({ children: [new TextRun({ text: r.summary, size: 19, color: "262626", font: FONT_KR })] })],
      }),
    ],
  }));
  return new Table({ width: { size: 9800, type: WidthType.DXA }, columnWidths: w, rows: [headerRow, ...bodyRows] });
}

// ───────────────────────── 버전 상세 블록 (P 팔레트, DemultiConfirm 형식) ─────────────────────────

/** "v1.2   2026-09-02   [내용 오류 수정]" 형태의 버전 헤더 줄 */
function versionHeader(version, date, tag, tagColor) {
  return new Paragraph({
    spacing: { after: 60, before: 420 },
    children: [
      new TextRun({ text: version, bold: true, color: P.navy, size: 34, font: FONT_CODE }),
      new TextRun({ text: "   ", size: 34 }),
      new TextRun({ text: date, color: P.gray, size: 22, font: FONT_KR }),
      new TextRun({ text: "   ", size: 22 }),
      new TextRun({ text: tag, bold: true, color: resolveColor(tagColor, P.primary), size: 20, font: FONT_KR }),
    ],
  });
}

/** 변경 항목 소제목 (예: "DEG 결과 복사 절차 명시") */
function changeHeading(text) {
  return new Paragraph({
    spacing: { after: 60, before: 160 },
    children: [new TextRun({ text, bold: true, color: P.primary, size: 21, font: FONT_KR })],
  });
}

/** 소제목 아래 설명 문단. segments에 run()/code()/b()로 만든 TextRun들을 섞어 넣는다. */
function bodyPara(segments) {
  return new Paragraph({ spacing: { after: 140 }, children: segments });
}

/** "**라벨** — 설명" 형태의 레벨0 불릿 (라벨 색으로 의미 구분: danger/success/warning/primary 등) */
function labelBullet(label, labelColor, text, level = 0) {
  return new Paragraph({
    numbering: { reference: "rn-bullets", level },
    spacing: { after: 70 },
    children: [
      new TextRun({ text: label, bold: true, color: resolveColor(labelColor, P.primary), size: 20, font: FONT_KR }),
      new TextRun({ text: " — ", color: P.gray, size: 20, font: FONT_KR }),
      new TextRun({ text, size: 20, font: FONT_KR }),
    ],
  });
}

/** 라벨 없는 일반 불릿. level=1이면 회색 하위 불릿(○)으로 축소 표시 */
function plainBullet(text, level = 0) {
  return new Paragraph({
    numbering: { reference: "rn-bullets", level },
    spacing: { after: level ? 60 : 70 },
    children: [new TextRun({ text, size: level ? 19 : 20, color: level ? P.grayDark : "111111", font: FONT_KR })],
  });
}

/**
 * 2열 비교/설명 표 (구분·표기 예 / 수정 전·수정 후 등).
 * @param {string[]} headers - 2개
 * @param {Array<[cellSpec, cellSpec]>} rows - cellSpec: string | {text, bold, color, code}
 * @param {number[]} widths - 기본 [2400,6600] (합계 9000)
 */
function compareTable(headers, rows, widths) {
  const w = widths || [4500, 4500];
  const cell = (spec, width) => {
    const s = typeof spec === "string" ? { text: spec } : spec;
    const font = s.code ? FONT_CODE : FONT_KR;
    const size = s.code ? 18 : 18;
    return new TableCell({
      width: { size: width, type: WidthType.DXA },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({ children: [new TextRun({
        text: s.text, bold: !!s.bold, italics: !!s.italics, font,
        size: s.size || size, color: s.color || (s.bold ? P.navy : P.black),
      })] })],
    });
  };
  const headerRow = new TableRow({ children: headers.map((h, i) => new TableCell({
    width: { size: w[i], type: WidthType.DXA },
    shading: { type: ShadingType.CLEAR, fill: P.primary },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: "FFFFFF", size: 19, font: FONT_KR })] })],
  })) });
  const bodyRows = rows.map((r) => new TableRow({ children: r.map((c, i) => cell(c, w[i])) }));
  return new Table({
    width: { size: w.reduce((a, x) => a + x, 0), type: WidthType.DXA },
    columnWidths: w,
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: "auto" },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: "auto" },
      left: { style: BorderStyle.SINGLE, size: 4, color: "auto" },
      right: { style: BorderStyle.SINGLE, size: 4, color: "auto" },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 4, color: "auto" },
      insideVertical: { style: BorderStyle.SINGLE, size: 4, color: "auto" },
    },
    rows: [headerRow, ...bodyRows],
  });
}

/** 표 뒤 여백용 빈 문단 (표와 다음 문단 사이 간격 보정) */
function spacer(after = 120) {
  return new Paragraph({ spacing: { after } });
}

/**
 * 하나의 버전 블록 전체를 조립.
 * @param {object} v
 * @param {string} v.version, v.date, v.tag, v.tagColor
 * @param {Array<object>} v.sections - 각 원소: { heading, paragraphs?, bullets?, table?, closingParas? }
 *   - paragraphs: TextRun[][] (각 원소가 한 문단의 segments)
 *   - bullets: Array<{label?, labelColor?, text, level?}>  (label 없으면 plainBullet)
 *   - table: { headers, rows, widths }
 */
function versionBlock(v) {
  const out = [];
  out.push(versionHeader(v.version, v.date, v.tag, v.tagColor));
  for (const sec of v.sections) {
    if (sec.heading) out.push(changeHeading(sec.heading));
    for (const p of sec.paragraphs || []) out.push(bodyPara(p));
    if (sec.table) {
      out.push(compareTable(sec.table.headers, sec.table.rows, sec.table.widths));
      out.push(spacer());
    }
    for (const bl of sec.bullets || []) {
      if (bl.label) out.push(labelBullet(bl.label, bl.labelColor, bl.text, bl.level || 0));
      else out.push(plainBullet(bl.text, bl.level || 0));
    }
  }
  return out;
}

// ───────────────────────── 부록/각주 (P 팔레트) ─────────────────────────

function sectionHeading(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    border: { bottom: { style: BorderStyle.SINGLE, color: P.primary, size: 6, space: 6 } },
    spacing: { before: 360, after: 160 },
    children: [new TextRun({ text, bold: true, color: P.primary, size: 30, font: FONT_KR })],
  });
}

function footnote(text) {
  return new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text, italics: true, color: P.gray, size: 17, font: FONT_KR })] });
}

// ───────────────────────── 헤더/푸터 ─────────────────────────

function makeHeader(rightText) {
  return new Header({ children: [new Paragraph({
    alignment: AlignmentType.RIGHT,
    children: [new TextRun({ text: rightText, color: P.gray, size: 16, font: FONT_KR })],
  })] });
}

function makeFooter(deptText) {
  return new Footer({ children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [
      new TextRun({ text: deptText + "  ·  ", color: P.gray, size: 16, font: FONT_KR }),
      new TextRun({ children: [PageNumber.CURRENT], color: P.gray, size: 16, font: FONT_KR }),
    ],
  })] });
}

// ───────────────────────── numbering 설정 ─────────────────────────

function numberingConfig() {
  return {
    config: [{
      reference: "rn-bullets",
      levels: [
        { level: 0, format: LevelFormat.BULLET, text: "●", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "○", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1440, hanging: 360 } } } },
      ],
    }],
  };
}

// ───────────────────────── 최종 Document 조립 ─────────────────────────

/**
 * @param {object} o
 * @param {object} o.frontMatter - frontMatter()에 넘길 옵션 그대로
 * @param {Array<object>} o.versions - versionBlock()에 넘길 버전 객체 배열. **최신 버전을 배열의 첫 원소로.**
 * @param {string} [o.headerText] - 페이지 상단 우측 텍스트 (예: "GSEA 분석 가이드 Release Note")
 * @param {string} [o.footerDept] - 페이지 하단 중앙 텍스트 (부서명 등)
 * @param {string} [o.footnoteText] - 문서 맨 아래 각주
 * @param {boolean} [o.pageSizeA4=true]
 */
function buildDocument(o) {
  const children = [];
  children.push(...frontMatter(o.frontMatter));
  children.push(divider());
  o.versions.forEach((v, i) => {
    children.push(...versionBlock(v));
    if (i < o.versions.length - 1) children.push(divider());
  });
  if (o.footnoteText) {
    children.push(divider());
    children.push(footnote(o.footnoteText));
  }

  const sectionProps = {
    properties: {
      page: {
        size: o.pageSizeA4 === false ? { width: 12240, height: 15840 } : { width: 11906, height: 16838 },
        margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 },
      },
    },
    children,
  };
  if (o.headerText) sectionProps.headers = { default: makeHeader(o.headerText) };
  if (o.footerDept) sectionProps.footers = { default: makeFooter(o.footerDept) };

  return new Document({
    styles: { default: { document: { run: { font: FONT_KR, size: 20 } } } },
    numbering: numberingConfig(),
    sections: [sectionProps],
  });
}

module.exports = {
  FONT_KR, FONT_CODE, P, F, TAG_COLORS,
  run, code, b, divider,
  frontMatter, summaryTable,
  versionHeader, changeHeading, bodyPara, labelBullet, plainBullet, compareTable, spacer, versionBlock,
  sectionHeading, footnote, makeHeader, makeFooter, numberingConfig,
  buildDocument,
  Packer,
};
