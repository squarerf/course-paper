# Course Paper Generator

自动生成课程论文的 Claude Code Skill。

## 功能特性

- **文献检索**：使用 Semantic Scholar MCP 搜索学术论文
- **文献验证**：使用 DOI Check MCP 批量验证文献真实性（必须在写正文前完成）
- **内容生成**：自动生成论文正文、中英文摘要
- **图表生成**：使用 Python matplotlib 生成11种标准图表
- **Word生成**：使用 Node.js docx 库生成带样式的Word文档
- **自动目录**：支持Word目录自动生成
- **图表选择**：支持 `--type`、`--count`、`--default` 筛选图表

## 触发条件

当用户说以下关键词时自动触发：
- "写论文"、"生成论文"、"课程论文"、"综述论文"
- "帮我写篇论文"、"论文生成"

## 默认格式

| 样式 | 中文字体 | 英文字体 | 字号 | 段落格式 |
|------|----------|----------|------|----------|
| 论文题目 | 黑体 | Times New Roman | 三号加粗 | 居中 |
| 一级标题 | 黑体 | Times New Roman | 三号加粗 | 左对齐、无缩进 |
| 二级标题 | 黑体 | Times New Roman | 四号加粗 | 左对齐、无缩进 |
| 正文 | 宋体 | Times New Roman | 四号 | 两端对齐、首行缩进2字符 |
| 参考文献 | 宋体 | Times New Roman | 小四 | Word自动编号[1] |

## 使用方法

1. 将整个 `course-paper/` 目录复制到 `~/.claude/skills/`
2. 在 Claude Code 中说"写论文"或"课程论文"
3. 按提示提供论文信息（题目、字数、文献数量等）
4. 等待自动生成完成

## 依赖工具

### MCP Servers
- `semantic-scholar` — 文献检索（工具：paper-search-advanced, papers-references 等）
- `doi-check` — 文献验证（工具：batchVerifyCitations, findVerifiedPapers 等）

### 软件依赖
- Python 3 + matplotlib + numpy（图表生成）
- Node.js + docx库（Word生成）

## 文件结构

```
course-paper/
├── SKILL.md                      # Skill 主文件（171行）
├── TASK_CHECKLIST.md             # 任务跟踪清单
├── README.md                     # 本文件
├── evals/
│   └── evals.json                # 测试用例
├── references/
│   ├── progress-templates.md     # 进度显示模板
│   ├── format-spec.md            # 字体/分页/对齐规范
│   ├── search-strategy.md        # 检索工具和策略
│   └── code-templates.md         # 脚本调用说明
└── scripts/
    ├── generate_docx.js          # Word文档生成脚本
    ├── generate_charts.py        # 图表生成脚本（11种类型）
    └── package.json              # Node.js 依赖配置
```

## 图表类型

`generate_charts.py` 支持11种图表：

| 类型 | 图表 | 用途 |
|------|------|------|
| `bar` | 柱状图 | 性能对比 |
| `radar` | 雷达图 | 多维对比 |
| `flow` | 流程图 | 技术演进 |
| `line` | 折线图 | 趋势/循环 |
| `area` | 面积图 | 文献趋势 |
| `pie` | 饼图 | 占比分析 |
| `scatter` | 散点图 | 相关性 |
| `heatmap` | 热力图 | 矩阵/系数 |
| `box` | 箱线图 | 分布统计 |
| `stacked_bar` | 堆叠柱状图 | 构成分析 |
| `violin` | 小提琴图 | 密度分布 |

## 执行流程

1. 收集需求信息
2. 默认格式规范
3. 文献检索
4. **文献真实性验证**（必须在写正文前完成）
5. 论文内容生成
6. 图表生成
7. Word文档生成
8. 输出检查
9. 交付

## 许可证

MIT
