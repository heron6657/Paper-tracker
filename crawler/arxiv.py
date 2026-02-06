# crawler/arxiv.py
import feedparser
from datetime import datetime, timedelta
import urllib.parse  # 新增：用于正确 URL 编码

from crawler.keywords import ARXIV_CORE_KEYWORDS


def build_query(keywords):
    """构建 arXiv 的 search_query 字符串（内部使用）"""
    # 每个关键词用 all:"关键词" 包裹，并用 AND 连接（更严格匹配）
    # 如果你想要更宽松的搜索，可以改成 ' OR '.join(...)
    parts = [f'all:"{kw}"' for kw in keywords]
    return ' OR '.join(parts)


def fetch_arxiv_papers(keywords=ARXIV_CORE_KEYWORDS, days=7, max_results=20):
    base_url = "http://export.arxiv.org/api/query?"

    # 1. 构建关键词部分查询
    kw_query = build_query(keywords)

    # 2. 计算日期范围（最近 days 天）
    end_date = datetime.utcnow()   # arXiv 用 UTC 时间
    start_date = end_date - timedelta(days=days)
    
    # 日期格式：YYYYMMDD（不需要小时，除非你特别精确）
    date_start = start_date.strftime("%Y%m%d")
    date_end   = end_date.strftime("%Y%m%d")
    
    date_filter = f'submittedDate:[{date_start} TO {date_end}]'

    # 3. 组合完整查询
    raw_query = f"({kw_query}) AND {date_filter}"

    # 4. 重要：完整 URL 编码（处理空格、"、() 等）
    encoded_query = urllib.parse.quote(raw_query)

    # 5. 拼接最终 URL
    url = (
        f"{base_url}"
        f"search_query={encoded_query}&"
        f"sortBy=submittedDate&"
        f"sortOrder=descending&"
        f"max_results={max_results}"
    )

    print("DEBUG arXiv URL:", url)
    # 你可以复制上面打印的 URL 到浏览器，看是否返回 <entry> 标签

    feed = feedparser.parse(url)

    papers = []
    for entry in feed.entries:
        # 使用 .get() 防止某些字段缺失时崩溃
        papers.append({
            "title": entry.get("title", "No title"),
            "authors": [a.name for a in entry.get("authors", [])],
            "abstract": entry.get("summary", "No abstract"),
            "link": entry.get("link", "No link"),
            "published": entry.get("published", "No date")
        })

    print(f"Total papers fetched from arXiv: {len(papers)}")
    
    if len(papers) == 0:
        print("No papers found. Possible reasons:")
        print("  - Keywords too strict → try changing AND to OR in build_query()")
        print("  - No new papers in last {days} days → increase days")
        print("  - Network/arXiv API issue → check the DEBUG URL in browser")

    return papers