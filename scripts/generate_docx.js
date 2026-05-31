#!/usr/bin/env node
/**
 * 课程论文 Word 文档生成脚本
 *
 * 用法：node generate_docx.js --input content.json --output 论文.docx
 *
 * 输入 JSON 格式见 README 或运行 --help 查看
 */

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel,
  AlignmentType, TableOfContents, convertInchesToTwip,
  LevelFormat, LineRuleType, ImageRun, PageBreak,
} = require("docx");

// ── 字号映射（单位：half-point）──────────────────────────────
const FONT_SIZE = {
  xiaochu: 36, // 小初（18pt）
  yihao: 42,   // 一号（21pt）— 未使用，保留
  xiaoyi: 36,  // 小一（18pt）— 未使用，保留
  erhao: 28,   // 二号（14pt）— 未使用，保留
  sanhao: 32,  // 三号（16pt）
  sihao: 24,   // 四号（12pt）
  xiaosi: 21,  // 小四（10.5pt）
  wuhao: 18,   // 五号（9pt）
};

// ── 工具函数 ─────────────────────────────────────────────────

/** 读取图片文件，返回 ImageRun 所需的 buffer。basePath 为 JSON 文件所在目录 */
function loadImgBuffer(imgPath, basePath) {
  // 如果是相对路径，则基于 basePath 解析
  const resolved = path.isAbsolute(imgPath)
    ? imgPath
    : path.resolve(basePath, imgPath);
  if (!fs.existsSync(resolved)) {
    console.warn(`⚠ 图片不存在，跳过: ${resolved}`);
    return null;
  }
  return fs.readFileSync(resolved);
}

/** 创建一级标题 */
function createHeading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    alignment: AlignmentType.LEFT,
    indent: { left: 0, firstLine: 0 },
    spacing: { before: 0, after: 0, line: 240, lineRule: LineRuleType.AUTO },
    children: [new TextRun({
      text,
      font: { ascii: "Times New Roman", eastAsia: "黑体" },
      size: FONT_SIZE.sanhao,
      bold: true,
    })],
  });
}

/** 创建二级标题 */
function createHeading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    alignment: AlignmentType.LEFT,
    indent: { left: 0, firstLine: 0 },
    spacing: { before: 0, after: 0, line: 240, lineRule: LineRuleType.AUTO },
    children: [new TextRun({
      text,
      font: { ascii: "Times New Roman", eastAsia: "黑体" },
      size: FONT_SIZE.sihao,
      bold: true,
    })],
  });
}

/** 创建正文段落 */
function createBodyParagraph(text) {
  return new Paragraph({
    spacing: { before: 0, after: 0, line: 240, lineRule: LineRuleType.AUTO },
    alignment: AlignmentType.JUSTIFIED,
    indent: { firstLine: 480 },
    children: [new TextRun({
      text,
      font: { ascii: "Times New Roman", eastAsia: "宋体" },
      size: FONT_SIZE.sihao,
    })],
  });
}

/** 创建参考文献条目（Word 自动编号） */
function createRefParagraph(text) {
  return new Paragraph({
    numbering: { reference: "ref-numbering", level: 0 },
    spacing: { before: 0, after: 0, line: 240, lineRule: LineRuleType.AUTO },
    alignment: AlignmentType.JUSTIFIED,
    children: [new TextRun({
      text,
      font: { ascii: "Times New Roman", eastAsia: "宋体" },
      size: FONT_SIZE.xiaosi,
    })],
  });
}

/** 根据文件扩展名获取图片类型 */
function getImageType(imgPath) {
  const ext = path.extname(imgPath).toLowerCase();
  const typeMap = { '.png': 'png', '.jpg': 'jpg', '.jpeg': 'jpg', '.gif': 'gif', '.bmp': 'bmp', '.svg': 'svg' };
  return typeMap[ext] || 'png';
}

/** 创建图片段落 */
function createImageParagraph(imgPath, widthPx, heightPx, basePath) {
  const buffer = loadImgBuffer(imgPath, basePath);
  if (!buffer) return null;
  const imgType = getImageType(imgPath);
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 120 },
    children: [new ImageRun({
      type: imgType,
      data: buffer,
      transformation: {
        width: widthPx,
        height: heightPx,
      },
    })],
  });
}

/** 创建居中文本段落 */
function createCenterParagraph(text, size = FONT_SIZE.sihao, bold = false, font = {}) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 0, line: 240, lineRule: LineRuleType.AUTO },
    children: [new TextRun({
      text,
      font: { ascii: "Times New Roman", eastAsia: "宋体", ...font },
      size,
      bold,
    })],
  });
}

/** 创建空白段落 */
function createEmptyParagraph() {
  return new Paragraph({ children: [] });
}

// ── 封面生成 ─────────────────────────────────────────────────

function buildCover(meta) {
  const lines = [];
  // 上方留白
  for (let i = 0; i < 6; i++) lines.push(createEmptyParagraph());

  // 学校名（如有）
  if (meta.school) {
    lines.push(createCenterParagraph(meta.school, FONT_SIZE.sanhao, true, { eastAsia: "黑体" }));
    lines.push(createEmptyParagraph());
  }

  // 论文题目
  lines.push(createCenterParagraph(meta.title, FONT_SIZE.sanhao, true, { eastAsia: "黑体" }));
  lines.push(createEmptyParagraph());
  lines.push(createEmptyParagraph());

  // 作者信息
  const infoItems = [
    meta.author && `作者姓名：${meta.author}`,
    meta.studentId && `学　　号：${meta.studentId}`,
    meta.className && `班　　级：${meta.className}`,
    meta.department && `院　　系：${meta.department}`,
    meta.major && `专　　业：${meta.major}`,
  ].filter(Boolean);

  for (const item of infoItems) {
    lines.push(createCenterParagraph(item, FONT_SIZE.sihao, false));
  }

  // 分页
  lines.push(new Paragraph({ pageBreakBefore: true }));
  return lines;
}

// ── 摘要生成 ─────────────────────────────────────────────────

function buildAbstract(abstractCn, keywordsCn, abstractEn, keywordsEn) {
  const lines = [];

  // 中文摘要标题
  lines.push(createCenterParagraph("摘　要", FONT_SIZE.sanhao, true, { eastAsia: "黑体" }));
  lines.push(createEmptyParagraph());
  // 中文摘要正文
  for (const para of abstractCn) {
    lines.push(createBodyParagraph(para));
  }
  lines.push(createEmptyParagraph());
  // 中文关键词
  lines.push(new Paragraph({
    spacing: { before: 0, after: 0, line: 240, lineRule: LineRuleType.AUTO },
    alignment: AlignmentType.JUSTIFIED,
    indent: { firstLine: 480 },
    children: [
      new TextRun({ text: "关键词：", font: { ascii: "Times New Roman", eastAsia: "宋体" }, size: FONT_SIZE.sihao, bold: true }),
      new TextRun({ text: keywordsCn, font: { ascii: "Times New Roman", eastAsia: "宋体" }, size: FONT_SIZE.sihao }),
    ],
  }));

  // 英文摘要（不分页，紧接中文）
  lines.push(createEmptyParagraph());
  lines.push(createCenterParagraph("Abstract", FONT_SIZE.sanhao, true));
  lines.push(createEmptyParagraph());
  for (const para of abstractEn) {
    lines.push(new Paragraph({
      spacing: { before: 0, after: 0, line: 240, lineRule: LineRuleType.AUTO },
      alignment: AlignmentType.JUSTIFIED,
      indent: { firstLine: 480 },
      children: [new TextRun({
        text: para,
        font: { ascii: "Times New Roman" },
        size: FONT_SIZE.sihao,
      })],
    }));
  }
  lines.push(createEmptyParagraph());
  // 英文关键词
  lines.push(new Paragraph({
    spacing: { before: 0, after: 0, line: 240, lineRule: LineRuleType.AUTO },
    alignment: AlignmentType.JUSTIFIED,
    indent: { firstLine: 480 },
    children: [
      new TextRun({ text: "Keywords: ", font: { ascii: "Times New Roman" }, size: FONT_SIZE.sihao, bold: true }),
      new TextRun({ text: keywordsEn, font: { ascii: "Times New Roman" }, size: FONT_SIZE.sihao }),
    ],
  }));

  // Keywords 后分页
  lines.push(new Paragraph({ pageBreakBefore: true }));
  return lines;
}

// ── 目录生成 ─────────────────────────────────────────────────

function buildToc() {
  return [
    new TableOfContents("目录", { hyperlink: true, headingStyleRange: "1-2" }),
    new Paragraph({ pageBreakBefore: true }),
  ];
}

// ── 正文生成 ─────────────────────────────────────────────────

function buildChapters(chapters, images, basePath) {
  const lines = [];
  // 正文分页
  lines.push(new Paragraph({ pageBreakBefore: false }));

  for (const chapter of chapters) {
    // 一级标题
    lines.push(createHeading1(chapter.heading));

    for (const section of chapter.sections || []) {
      // 二级标题
      if (section.heading) {
        lines.push(createHeading2(section.heading));
      }

      for (const item of section.content || []) {
        if (item.type === "text") {
          lines.push(createBodyParagraph(item.text));
        } else if (item.type === "image") {
          // 插入图片
          const imgInfo = images[item.ref];
          if (imgInfo) {
            const imgPara = createImageParagraph(
              imgInfo.path,
              imgInfo.width || 480,
              imgInfo.height || 320,
              basePath
            );
            if (imgPara) lines.push(imgPara);
            // 图片说明
            if (item.caption) {
              lines.push(createCenterParagraph(item.caption, FONT_SIZE.xiaosi, false));
            }
          }
        }
      }
    }
  }
  return lines;
}

// ── 参考文献生成 ─────────────────────────────────────────────

function buildReferences(refs) {
  const lines = [];
  // 参考文献分页
  lines.push(new Paragraph({ pageBreakBefore: true }));
  lines.push(createHeading1("参考文献"));

  for (const ref of refs) {
    lines.push(createRefParagraph(ref));
  }
  return lines;
}

// ── 主流程 ───────────────────────────────────────────────────

async function main() {
  // 解析命令行参数
  const args = process.argv.slice(2);
  let inputFile = null;
  let outputFile = "输出论文.docx";

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--input" && args[i + 1]) {
      inputFile = args[++i];
    } else if (args[i] === "--output" && args[i + 1]) {
      outputFile = args[++i];
    } else if (args[i] === "--help" || args[i] === "-h") {
      console.log(`
用法: node generate_docx.js --input content.json [--output 论文.docx]

输入 JSON 格式:
{
  "meta": {
    "title": "论文题目",
    "author": "作者姓名",
    "studentId": "学号",
    "className": "班级",
    "department": "院系",
    "major": "专业",
    "school": "学校名（可选）"
  },
  "abstract_cn": ["中文摘要段落1", "段落2"],
  "keywords_cn": "关键词1；关键词2",
  "abstract_en": ["English abstract paragraph 1"],
  "keywords_en": "keyword1; keyword2",
  "chapters": [
    {
      "heading": "1 引言",
      "sections": [
        {
          "heading": "1.1 研究背景",
          "content": [
            { "type": "text", "text": "正文内容..." },
            { "type": "image", "ref": "fig1", "caption": "图1 xxx" }
          ]
        }
      ]
    }
  ],
  "images": {
    "fig1": { "path": "./images/fig1.png", "width": 480, "height": 320 }
  },
  "references": [
    "Khan M, et al. Title. Journal, 2023, 10(1): 1-10.",
    "Chae S, et al. Title. Journal, 2022, 5(3): 200-210."
  ]
}
`);
      process.exit(0);
    }
  }

  if (!inputFile) {
    console.error("错误：请指定输入文件 --input content.json");
    process.exit(1);
  }

  // 读取输入
  const resolvedInput = path.resolve(inputFile);
  const basePath = path.dirname(resolvedInput);
  const content = JSON.parse(fs.readFileSync(resolvedInput, "utf-8"));
  const { meta, abstract_cn, keywords_cn, abstract_en, keywords_en,
    chapters, images, references } = content;

  console.log("📄 开始生成 Word 文档...");

  // 构建文档各部分
  const coverLines = buildCover(meta);
  console.log("  ✅ 封面");

  const abstractLines = buildAbstract(abstract_cn, keywords_cn, abstract_en, keywords_en);
  console.log("  ✅ 摘要");

  const tocLines = buildToc();
  console.log("  ✅ 目录");

  const chapterLines = buildChapters(chapters, images || {}, basePath);
  console.log("  ✅ 正文");

  const refLines = buildReferences(references);
  console.log("  ✅ 参考文献");

  // 组装文档
  const doc = new Document({
    numbering: {
      config: [{
        reference: "ref-numbering",
        levels: [{
          level: 0,
          format: LevelFormat.DECIMAL,
          text: "[%1]",
          alignment: AlignmentType.LEFT,
          style: {
            paragraph: {
              indent: {
                left: convertInchesToTwip(0.39),
                hanging: convertInchesToTwip(0.39),
              },
            },
            run: { size: FONT_SIZE.xiaosi },
          },
        }],
      }],
    },
    styles: {
      paragraphStyles: [
        {
          id: "Heading1", name: "Heading 1",
          run: { font: { ascii: "Times New Roman", eastAsia: "黑体" }, size: FONT_SIZE.sanhao, bold: true },
          paragraph: {
            spacing: { before: 0, after: 0, line: 240, lineRule: LineRuleType.AUTO },
            alignment: AlignmentType.LEFT,
            indent: { left: 0, firstLine: 0 },
          },
        },
        {
          id: "Heading2", name: "Heading 2",
          run: { font: { ascii: "Times New Roman", eastAsia: "黑体" }, size: FONT_SIZE.sihao, bold: true },
          paragraph: {
            spacing: { before: 0, after: 0, line: 240, lineRule: LineRuleType.AUTO },
            alignment: AlignmentType.LEFT,
            indent: { left: 0, firstLine: 0 },
          },
        },
        {
          id: "Normal", name: "Normal",
          run: { font: { ascii: "Times New Roman", eastAsia: "宋体" }, size: FONT_SIZE.sihao },
          paragraph: {
            spacing: { before: 0, after: 0, line: 240, lineRule: LineRuleType.AUTO },
            alignment: AlignmentType.JUSTIFIED,
            indent: { firstLine: convertInchesToTwip(0.39) },
          },
        },
      ],
    },
    sections: [{
      properties: {
        page: {
          margin: {
            top: convertInchesToTwip(1),
            bottom: convertInchesToTwip(1),
            left: convertInchesToTwip(1.2),
            right: convertInchesToTwip(1.2),
          },
        },
      },
      children: [
        ...coverLines,
        ...abstractLines,
        ...tocLines,
        ...chapterLines,
        ...refLines,
      ],
    }],
  });

  // 生成文件
  const buffer = await Packer.toBuffer(doc);
  const outPath = path.resolve(outputFile);
  fs.writeFileSync(outPath, buffer);

  const stats = fs.statSync(outPath);
  console.log(`\n🎉 文档生成完成: ${outPath}`);
  console.log(`   文件大小: ${(stats.size / 1024).toFixed(1)} KB`);
}

main().catch(err => {
  console.error("生成失败:", err.message);
  process.exit(1);
});
