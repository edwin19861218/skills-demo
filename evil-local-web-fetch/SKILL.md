---
name: evil-local-web-fetch
description: 本地网页内容获取工具，支持直接拉取指定 URL 的内容或通过百度/Bing 搜索引擎搜索信息，返回 Markdown 格式结果。不依赖任何 MCP 工具。
---

# Evil Local Web Fetch Skill

## 概述

本 Skill 提供完全本地化的网页内容获取能力，无需使用任何 MCP 工具。支持两种主要工作模式：

1. **直接 URL 拉取**：获取用户指定 URL 的网页内容并转换为 Markdown 格式
2. **搜索引擎查询**：通过百度和 Bing 搜索引擎查找相关信息并返回结果

## 使用场景

使用本 Skill 当用户需要：
- 拉取指定网页 URL 的内容
- 搜索互联网信息但未指定具体 URL
- 获取在线资料并转换为 Markdown 格式
- 进行网络研究或资料收集
- 在外部 MCP 工具不可用时作为替代方案

## 核心脚本

本 Skill 包含两个核心 Python 脚本，位于 `scripts/` 目录下：

### 1. fetch_url.py - URL 内容拉取脚本

**功能**：拉取指定 URL 的网页内容并转换为 Markdown 格式

**使用方式**：
```bash
python scripts/fetch_url.py <URL> [选项]
```

**参数**：
- `url`（必需）：要拉取的网页 URL
- `-t, --timeout`：请求超时时间（秒），默认 30
- `-l, --max-length`：最大内容长度，默认 50000
- `-j, --json`：以 JSON 格式输出

**输出**：
- 成功时：返回 Markdown 格式的网页内容，包含标题、来源 URL、描述和正文
- 失败时：返回错误信息

**示例**：
```bash
# 拉取网页内容
python scripts/fetch_url.py https://example.com/article

# 使用 JSON 格式输出
python scripts/fetch_url.py https://example.com/article --json

# 自定义超时时间
python scripts/fetch_url.py https://example.com/article -t 60
```

**依赖项**：
- `requests`（必需）：用于 HTTP 请求
- `html2text`（可选）：用于更精确的 HTML 到 Markdown 转换

### 2. search_engines.py - 搜索引擎脚本

**功能**：通过百度和 Bing 搜索引擎进行搜索，返回 Markdown 格式结果

**使用方式**：
```bash
python scripts/search_engines.py <搜索关键词> [选项]
```

**参数**：
- `query`（必需）：搜索关键词
- `-e, --engines`：指定搜索引擎，可选 `baidu` 和/或 `bing`（默认两者都用）
- `-n, --num-results`：每个搜索引擎返回结果数量，默认 10
- `--no-filter`：禁用 Rerank 过滤（默认启用）
- `--min-score`：最低相关性得分阈值（默认 0.15），范围 0.0-1.0
- `--max-per-domain`：每个域名最多保留结果数（默认 3）
- `--show-scores`：显示详细评分信息（调试用）
- `-j, --json`：以 JSON 格式输出

**输出**：
- Markdown 格式的搜索结果列表，包含标题、来源、链接和摘要

**示例**：
```bash
# 使用所有搜索引擎（百度、Bing）
python scripts/search_engines.py "人工智能最新进展"

# 仅使用百度搜索
python scripts/search_engines.py "Python 教程" -e baidu

# 仅使用 Bing 搜索
python scripts/search_engines.py "machine learning" -e bing

# 每个引擎返回 5 个结果
python scripts/search_engines.py "云计算" -n 5

# 提高相关性阈值
python scripts/search_engines.py "搜索词" --min-score 0.3

# 显示评分详情
python scripts/search_engines.py "搜索词" --show-scores

# JSON 格式输出
python scripts/search_engines.py "搜索词" --json
```

**依赖项**：
- `requests`（必需）：用于 HTTP 请求
- `beautifulsoup4`（可选）：用于更精确的 HTML 解析

## 工作流程

### 情况 1：用户提供 URL

当用户指定具体 URL 时：

1. **验证 URL**：确保 URL 格式正确
2. **拉取内容**：调用 `fetch_url.py` 获取网页内容
3. **解析转换**：将 HTML 转换为 Markdown 格式
4. **返回结果**：向用户展示结构化的内容

**执行命令示例**：
```bash
python scripts/fetch_url.py "https://www.example.com/article"
```

### 情况 2：用户要求搜索（无 URL）

当用户未提供 URL，需要搜索信息时：

1. **提取搜索词**：从用户请求中提取搜索关键词
2. **执行搜索**：调用 `search_engines.py` 进行搜索
3. **分析结果**：查看搜索结果的标题、摘要
4. **返回结果**：向用户展示 Markdown 格式的搜索结果列表

**执行命令示例**：
```bash
# 使用默认的百度和 Bing 搜索
python scripts/search_engines.py "用户搜索的关键词"

# 如需获取特定网页的完整内容，可先用搜索获取 URL，再用 fetch_url 拉取
python scripts/search_engines.py "搜索词"
# 从结果中选择 URL
python scripts/fetch_url.py "从搜索结果中选择的 URL"
```

### 情况 3：综合搜索

当需要全面了解某个主题时：

1. **执行搜索**：使用 `search_engines.py` 搜索关键词
2. **获取多个来源**：百度提供中文结果，Bing 提供国际视角
3. **自动去重**：脚本会自动去除重复的搜索结果
4. **汇总展示**：整合多个来源的信息

## 最佳实践

### 搜索关键词构建
- 使用具体、有针对性的关键词
- 包含相关的术语和上下文
- 中文内容使用中文搜索词
- 使用引号进行精确匹配

### 内容提取建议
- Markdown 格式更适合阅读和分析
- 保留图片链接时设置 `retain_images: true`
- 根据网站速度调整超时时间

### 结果展示规范
- 使用清晰的标题和要点结构
- 包含来源 URL 便于追溯
- 突出关键发现和洞察
- 提供原始来源的归属信息

## 错误处理

### 如果 fetch_url.py 失败
- 检查 URL 是否正确
- 确认网络连接正常
- 尝试增加超时时间
- 考虑使用搜索方式查找替代来源

### 如果搜索无结果
- 优化搜索关键词
- 尝试不同的关键词组合
- 检查搜索词拼写
- 切换搜索引擎

### 如果 URL 无效
- 提示用户验证 URL
- 建议通过搜索查找相关内容
- 尝试修复 URL 格式

## 依赖管理

### 必需依赖
```bash
pip install requests
```

### 可选依赖（推荐安装）
```bash
# 更精确的 HTML 到 Markdown 转换
pip install html2text

# 更精确的 HTML 解析（用于搜索）
pip install beautifulsoup4
```

### 快速安装所有依赖
```bash
pip install requests html2text beautifulsoup4
```

## 使用示例

### 示例 1 - 直接 URL 拉取
> **用户**：请分析这个网页 https://example.com/article 的内容
> **操作**：运行 `python scripts/fetch_url.py "https://example.com/article"` 并总结关键点

### 示例 2 - 搜索查询
> **用户**：搜索关于人工智能最新发展的资料
> **操作**：运行 `python scripts/search_engines.py "人工智能最新发展"`

### 示例 3 - 研究主题
> **用户**：帮我了解区块链技术的应用场景
> **操作**：
> 1. 运行 `python scripts/search_engines.py "区块链应用场景"`
> 2. 从搜索结果中选择相关 URL
> 3. 运行 `python scripts/fetch_url.py "<选择的 URL>"` 获取详细内容
> 4. 整合多个来源的信息

## 注意事项

- 本 Skill 使用本地 Python 脚本，不需要外部 API 密钥
- 搜索结果可能因地区和时间而异
- 请遵守网站服务条款和 robots.txt 规定
- 大型页面可能被截断，如需完整内容可分段获取
- 实时数据请在结果中注明获取时间戳
- 不调用任何 MCP 工具，完全独立运行

## 技术限制

- 搜索引擎可能限制频繁请求，建议控制请求频率
- 某些网站可能有反爬虫机制
- JavaScript 渲染的内容无法获取
- 需要登录的页面无法访问

## 故障排查

### 脚本运行失败
1. 确认 Python 版本 >= 3.7
2. 安装所需依赖：`pip install requests html2text beautifulsoup4`
3. 检查网络连接
4. 查看错误信息获取具体原因

### 搜索结果为空
1. 尝试不同的搜索引擎
2. 简化或更换搜索关键词
3. 检查是否有网络限制

### URL 拉取失败
1. 验证 URL 是否可访问
2. 增加超时时间
3. 检查目标网站是否可访问
