# Paper-Tracker

一个面向 **UAV / 多模态感知** 方向的 arXiv 论文追踪工具。

自动从 arXiv 抓取最新论文 → 硬规则过滤 → LLM 质量评分 → 融合策略分类 → 生成 Markdown 报告。

## 功能流程

```
arXiv API ──► hard_filter ──► LLM 评分 ──► 融合分类 ──► Markdown 报告
                  │              (可选)        (可选)
                  └── 字数/结构/相关性过滤
```

## 目录结构

```
Paper-tracker/
├── main.py                   # 入口
├── config.py                 # 配置（关键词、阈值、路径开关）
├── crawler/
│   ├── arxiv.py              # arXiv API 抓取
│   └── keywords.py           # 搜索关键词
├── analyzer/
│   ├── hard_filter.py        # 规则过滤
│   ├── quality_scorer.py     # LLM 论文打分
│   ├── aggregate.py          # 分数聚合
│   ├── quality_pipeline.py   # 评估主流程
│   └── fusion_classifier.py  # 融合策略分类
├── reporter/
│   └── markdown.py           # Markdown 报告生成
└── data/
    ├── paper_store.py        # 论文 JSON 存储/去重合并
    └── papers.json           # 论文数据库
```

## 安装

```bash
pip install -r requirements.txt
```

## 使用

不调用 LLM（仅硬过滤），直接运行：

```bash
python main.py
```

启用 LLM 评分和融合分类：

```bash
export OPENAI_API_KEY=sk-xxx
python main.py
```

也可以将 key 写在项目根目录的 `.env` 中：

```
OPENAI_API_KEY=sk-xxx
```

## 输出

- `data/papers.json`：论文数据库（自动按 link 去重合并）
- `outputs/report.md`：Markdown 报告

## 配置

在 `config.py` 中调整：

- `ARXIV_DAYS`：抓取最近多少天
- `MAX_RESULTS`：单次抓取上限
- `QUALITY_LEVEL_KEEP`：哪些质量等级会进入报告
- `ENABLE_FUSION_CLASSIFY`：是否启用融合分类（需要 LLM）

关键词在 `crawler/keywords.py`（`ARXIV_CORE_KEYWORDS`）中调整。
