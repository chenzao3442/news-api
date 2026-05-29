# 新闻聚合Bot — LangGraph 工作流

## 项目概述
- **名称**: 新闻聚合Bot
- **功能**: 3个工作流分别抓取科技新闻、财经新闻、社会热点，统一输出 JSON 格式供 Bot LLM 生成中文简报

## 架构
```
用户请求 → 主图(graph.py) → dispatch条件路由 → 分支子图(并行HTTP请求) → merge合并 → 统一输出
```

## 节点清单

### 主调度图 (graph.py)

| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 |
|-------|---------|------|---------|---------|
| dispatch_node | `graph.py` | condition | 根据 workflow 字段路由 | "tech_news"→科技新闻分支, "finance_news"→财经新闻分支, "social_news"→社会热点分支 |

### 科技新闻分支

| 节点名 | 文件位置 | 类型 | 功能描述 | 备选方案 |
|-------|---------|------|---------|---------|
| hn_node | `nodes/hn_node.py` | task | 抓取 Hacker News 热门 | 失败降级到 hnrss.org RSS |
| github_node | `nodes/github_node.py` | task | 抓取 GitHub Trending | 失败降级到 GitHubTrendingRSS |
| hf_node | `nodes/hf_node.py` | task | 抓取 HuggingFace Papers | 失败返回空 |
| merge_tech_node | `nodes/merge_tech_node.py` | task | 合并三个科技来源 | - |

### 财经新闻分支

| 节点名 | 文件位置 | 类型 | 功能描述 | 备选方案 |
|-------|---------|------|---------|---------|
| wallstreet_node | `nodes/wallstreet_node.py` | task | 抓取华尔街见闻 | 被拦截返回空 |
| kr36_node | `nodes/kr36_node.py` | task | 抓取36氪快讯 | 失败降级到 RSS |
| merge_finance_node | `nodes/merge_finance_node.py` | task | 合并两个财经来源 | - |

### 社会热点分支

| 节点名 | 文件位置 | 类型 | 功能描述 | 备选方案 |
|-------|---------|------|---------|---------|
| weibo_node | `nodes/weibo_node.py` | task | 抓取微博热搜 | 被拦截返回空 |
| v2ex_node | `nodes/v2ex_node.py` | task | 抓取V2EX热门 | 失败降级到 RSS |
| merge_social_node | `nodes/merge_social_node.py` | task | 合并两个社会热点来源 | - |

## 工作流输入/输出

### 输入
```json
{ "workflow": "tech_news" | "finance_news" | "social_news" }
```

### 输出
```json
{
  "news_items": [
    {
      "source": "来源名",
      "title": "标题",
      "url": "链接",
      "heat": "热度",
      "time": "时间"
    }
  ]
}
```

## 状态定义
- **文件**: `state.py`
- **全局状态**: `GlobalState`（含所有工作流的 HTTP 结果字段 + news_items）
- **图输入**: `GraphInput(workflow)`
- **图输出**: `GraphOutput(news_items)`
- **每个节点有独立的 Input/Output 类型**

## 运行测试
```python
from graphs.graph import main_graph
main_graph.invoke({"workflow": "tech_news"})    # 科技新闻
main_graph.invoke({"workflow": "finance_news"}) # 财经新闻  
main_graph.invoke({"workflow": "social_news"})  # 社会热点
```