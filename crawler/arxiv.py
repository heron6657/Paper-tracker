# crawler/arxiv.py
import feedparser
from datetime import datetime, timedelta


from crawler.keywords import ARXIV_CORE_KEYWORDS

def build_query():
    return " AND ".join(ARXIV_CORE_KEYWORDS)





def fetch_arxiv_papers(keywords, days=1, max_results=20):
    base_url = "http://export.arxiv.org/api/query?"

    # 
    search_query = "+AND+".join([f'all:"{kw}"' for kw in keywords])

    url = (
        f"{base_url}"
        f"search_query={search_query}"
        f"&sortBy=submittedDate"
        f"&sortOrder=descending"
        f"&max_results={max_results}"
    )

    print("DEBUG arXiv URL:", url)

    feed = feedparser.parse(url)

    papers = []
    for entry in feed.entries:
        papers.append({
            "title": entry.title,
            "authors": [a.name for a in entry.authors],
            "abstract": entry.summary,
            "link": entry.link,
            "published": entry.published
        })

    return papers
