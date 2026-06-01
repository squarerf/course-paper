# 脚本调用说明

## 环境准备

```bash
# Node.js 依赖
cd <skill目录>/scripts
npm init -y && npm install docx

# Python 依赖（使用可用的 Python 命令）
pip install matplotlib numpy
# 或
pip3 install matplotlib numpy
```

**Python 路径检测：**
- Windows 上 `python` 可能指向 Windows Store stub（0字节），需要用 `python3` 或 `py`
- 脚本已内置编码修复（Windows GBK → UTF-8）和依赖检测

## Word 文档生成

**脚本路径：** `scripts/generate_docx.js`

**用法：**
```bash
# 基本用法
node scripts/generate_docx.js --input content.json --output 论文.docx

# 使用封面模板（可选）
node scripts/generate_docx.js --input content.json --output 论文.docx --cover 封面.docx

# 查看帮助
node scripts/generate_docx.js --help
```

**输入文件 `content.json` 格式：**
```json
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
  // images 字段说明：
  // - key 必须与 content 中 "type":"image" 的 "ref" 一致
  // - path 相对于 content.json 文件的位置
  // - width/height 单位为像素，用于 Word 中的图片缩放
  "references": [
    "Khan M, et al. Title. Journal, 2023, 10(1): 1-10.",
    "Chae S, et al. Title. Journal, 2022, 5(3): 200-210."
  ]
}
```

**支持的结构：**
- 封面（自动排版学校名、题目、作者信息）
- 中英文摘要（Keywords 后自动分页）
- 目录（可更新域）
- 正文（一级/二级标题 + 正文段落 + 图片插入）
- 参考文献（自动编号 [1][2]...）

---

## 图表生成

**脚本路径：** `scripts/generate_charts.py`

**用法：**
```bash
# 完整生成（JSON中所有图表）
python scripts/generate_charts.py --input charts.json --output ./images/

# 指定类型（从JSON中筛选）
python scripts/generate_charts.py -i charts.json -t bar,line,pie -o ./images/

# 指定数量（截取前N个）
python scripts/generate_charts.py -i charts.json -n 3 -o ./images/

# 默认模式（标准5图：柱状、雷达、流程、折线、面积）
python scripts/generate_charts.py -i charts.json --default -o ./images/

# 混合（指定类型 + 限制数量）
python scripts/generate_charts.py -i charts.json -t heatmap,box -n 2 -o ./images/
```

**输入文件 `charts.json` 格式：**
```json
{
  "charts": [
    {
      "type": "bar",
      "description": "材料性能对比",
      "data": {
        "title": "不同材料性能对比",
        "xlabel": "材料类型",
        "ylabel": "比容量 (mAh/g)",
        "categories": ["Si", "Graphite", "SiO", "Li4Ti5O12"],
        "series": [
          {"name": "理论比容量", "values": [4200, 372, 1600, 175]},
          {"name": "实际比容量", "values": [3000, 340, 1200, 160]}
        ],
        "colors": ["#2196F3", "#FF9800"]
      }
    },
    {
      "type": "radar",
      "description": "多维性能对比",
      "data": { ... }
    },
    {
      "type": "flow",
      "description": "技术演进图",
      "data": { ... }
    },
    {
      "type": "line",
      "description": "循环性能对比",
      "data": { ... }
    },
    {
      "type": "area",
      "description": "文献趋势分析",
      "data": { ... }
    }
  ]
}
```

**11种图表类型：**

| type | 图表 | 说明 |
|------|------|------|
| `bar` | 柱状图 | 材料性能对比，支持多组数据 |
| `radar` | 雷达图 | 多维性能对比，支持多材料 |
| `flow` | 流程图 | 技术演进/机理示意图 |
| `line` | 折线图 | 循环性能/时间序列数据 |
| `area` | 面积图 | 文献趋势/累积数据 |
| `pie` | 饼图 | 占比分析（市场份额、组成比例） |
| `scatter` | 散点图 | 相关性分析、数据分布 |
| `heatmap` | 热力图 | 性能矩阵、相关系数 |
| `box` | 箱线图 | 数据分布、离群值检测 |
| `stacked_bar` | 堆叠柱状图 | 多维占比对比、构成分析 |
| `violin` | 小提琴图 | 分布密度、工艺条件对比 |

**输出：**
- PNG 图片（300dpi）
- `chart_summary.json` 汇总文件（含各图路径）
