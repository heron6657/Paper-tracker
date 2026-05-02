import os
from datetime import datetime

from tqdm import tqdm

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from crawler.arxiv import fetch_arxiv_papers
from crawler.keywords import ARXIV_CORE_KEYWORDS
from analyzer.quality_pipeline import evaluate_paper
from analyzer.fusion_classifier import classify_fusion
from reporter.markdown import generate_markdown
from data.paper_store import load_paper_db, save_paper_db, merge_papers
from config import (
    ARXIV_DAYS,
    MAX_RESULTS,
    QUALITY_LEVEL_KEEP,
    DATA_DIR,
    OUTPUT_DIR,
    PAPERS_PATH,
    REPORT_PATH,
    ENABLE_FUSION_CLASSIFY,
)


def _parse_published(value: str) -> datetime:
    if not value:
        return datetime.min
    for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return datetime.min


def analyze_paper(paper: dict, use_llm: bool) -> dict:
    """对单篇论文做硬过滤 + (可选)LLM 评分 + (可选)融合分类。"""
    if "quality" not in paper:
        paper["quality"] = evaluate_paper(paper)

    if use_llm and ENABLE_FUSION_CLASSIFY and "fusion" not in paper:
        if paper["quality"]["level"] != "Rejected":
            paper["fusion"] = classify_fusion(paper["abstract"])
        else:
            paper["fusion"] = "N/A"
    elif "fusion" not in paper:
        paper["fusion"] = "Unknown"

    return paper


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    use_llm = bool(os.getenv("OPENAI_API_KEY"))
    print(f"OPENAI_API_KEY {'已设置' if use_llm else '未设置'}，"
          f"{'启用' if use_llm else '跳过'} LLM 评分/融合分类")

    # 1. 加载已有数据库（用于去重）
    db = load_paper_db(PAPERS_PATH)
    print(f"已有论文数据库：{len(db)} 篇")
    existing_links = {p.get("link") for p in db}

    # 2. 抓取最新论文
    print(f"从 arXiv 抓取最近 {ARXIV_DAYS} 天的论文...")
    fetched = fetch_arxiv_papers(
        keywords=ARXIV_CORE_KEYWORDS,
        days=ARXIV_DAYS,
        max_results=MAX_RESULTS,
    )
    new_papers = [p for p in fetched if p.get("link") not in existing_links]
    print(f"本次抓取 {len(fetched)} 篇，去重后新增 {len(new_papers)} 篇")

    # 3. 对新论文做评估
    if new_papers:
        print("评估新论文...")
        for paper in tqdm(new_papers, desc="Evaluating"):
            try:
                analyze_paper(paper, use_llm=use_llm)
            except Exception as e:
                print(f"  评估失败（{paper.get('title','?')[:50]}...）: {e}")
                paper["quality"] = {
                    "final_score": 0,
                    "level": "Error",
                    "confidence": "low",
                    "reason": f"Evaluation error: {e}",
                }
                paper["fusion"] = "Unknown"

    # 4. 合并并持久化
    db = merge_papers(db, new_papers)
    save_paper_db(db, PAPERS_PATH)
    print(f"数据库已更新，共 {len(db)} 篇 -> {PAPERS_PATH}")

    # 5. 选出要进入报告的论文
    kept = [p for p in db if (p.get("quality") or {}).get("level") in QUALITY_LEVEL_KEEP]
    kept.sort(key=lambda p: _parse_published(p.get("published", "")), reverse=True)
    print(f"按质量过滤后保留 {len(kept)} 篇用于报告")

    # 6. 生成 Markdown 报告
    md = generate_markdown(kept, keywords=ARXIV_CORE_KEYWORDS, days=ARXIV_DAYS)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"报告已保存到: {REPORT_PATH}")


if __name__ == "__main__":
    main()
