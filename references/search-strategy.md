# 文献检索策略

## 可用工具

| 工具 | 用途 | 优先级 |
|------|------|--------|
| Semantic Scholar MCP | 主力搜索、DOI验证 | 高 |
| DOI Check MCP | 文献真实性验证 | 高 |
| WebSearch | 补充搜索、中文文献 | 中 |
| WebFetch | 抓取网页内容 | 中 |

## Semantic Scholar MCP 工具

服务器名：`semantic-scholar`

| 工具名 | 用途 | 参数 |
|--------|------|------|
| `papers-search-basic` | 基本搜索 | query, limit |
| `paper-search-advanced` | 高级搜索 | query, yearStart, yearEnd, minCitations, sortBy, limit |
| `search-paper-title` | 按标题精确搜索 | title, yearStart, yearEnd |
| `get-paper-abstract` | 获取论文摘要 | paperId |
| `papers-batch` | 批量查询论文详情 | paperIds (DOI/arXiv ID数组) |
| `search-arxiv` | arXiv搜索 | query, maxResults |
| `papers-references` | 查看论文参考文献 | paperId, limit |
| `papers-citations` | 查看引用该论文的文献 | paperId, limit |

## DOI Check MCP 工具

服务器名：`doi-check`

| 工具名 | 用途 | 参数 |
|--------|------|------|
| `verifyCitation` | 验证单篇文献 | title, authors, year, doi |
| `batchVerifyCitations` | 批量验证文献 | citations数组 |
| `findVerifiedPapers` | 搜索已验证的真实文献 | query, limit, yearFrom, yearTo |

## 检索流程

### 第一轮：Semantic Scholar 高精度搜索

使用 `paper-search-advanced` 按细分方向搜索：
- 5-8个关键词组合
- 筛选条件：年份 + 最低引用量
- 目标：收集 50-80 篇候选文献

### 第二轮：引用链追溯

使用 `papers-references` 追溯高引论文的参考文献：
- 补充经典文献 10-15 篇

### 第三轮：中文文献补充

使用 WebSearch 搜索中文综述和学位论文：
- 补充中文文献 5-10 篇

## 文献真实性验证（必须！）

**在写正文之前，必须验证所有文献的真实性。**

1. 提取每篇文献的标题、作者、年份、DOI
2. 调用 `batchVerifyCitations` 批量验证
3. 对于未通过验证的文献：
   - 有 DOI 的：用 `verifyCitation` 单独验证
   - 无 DOI 的：用 `findVerifiedPapers` 搜索替代文献
4. 删除所有无法验证的文献
5. 只保留验证通过的文献用于正文写作

**重要：不要编造 DOI！** 如果不确定 DOI，用 `findVerifiedPapers` 搜索获取真实 DOI。

## 筛选标准

- 引用量 > 50（>100为佳）
- 近3年文献占50%以上
- 每个子方向至少1篇
- 100% 通过 DOI 验证
