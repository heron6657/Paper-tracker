import json
import os
from typing import List, Dict

import numpy as np
from tqdm import tqdm
from datetime import date, datetime

from crawler.arxiv import fetch_arxiv_papers
from analyzer.quality_pipeline import evaluate_paper
from reporter.markdown import generate_markdown
from data.paper_store import load_paper_db, save_paper_db


from config import QUALITY_LEVEL_KEEP
from crawler.keywords import ARXIV_CORE_KEYWORDS


def load_or_fetch_papers(
    json_path: str,
    days: int = 30,          
    max_results: int = 50    
) -> List[Dict]:
    """
    如果 papers.json 存在 → 直接加载
    如果不存在 → 从 arXiv fetch 并保存到 json
    """
    if os.path.exists(json_path):
        print(f"从 {json_path} 加载已有论文...")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("papers.json 格式错误，最外层应为 list")
        print(f"共加载 {len(data)} 篇论文")
        return data

    else:
        print(f"{json_path} 不存在，正在从 arXiv 抓取论文（最近 {days} 天）...")
        try:
            papers = fetch_arxiv_papers(
                keywords=ARXIV_CORE_KEYWORDS,
                days=days,
                max_results=max_results
            )
            if not papers:
                print("警告：本次抓取 0 篇论文。请检查 crawler/arxiv.py 中的查询逻辑、关键词或网络。")
                return []

            # 确保 data 目录存在
            os.makedirs(os.path.dirname(json_path), exist_ok=True)

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(papers, f, ensure_ascii=False, indent=4)

            print(f"成功抓取并保存 {len(papers)} 篇论文到 {json_path}")
            return papers

        except Exception as e:
            print(f"抓取失败：{e}")
            return []


def clean_text(text: str) -> str:
    if text is None:
        return ""
    text = text.replace("\n", " ").replace("\t", " ")
    text = " ".join(text.split())
    return text.strip()


def build_document(paper: Dict) -> str:
    # 这个函数现在仅用于 embeddings，不再用于报告输出
    title = clean_text(paper.get("title", ""))
    abstract = clean_text(paper.get("abstract", ""))
    authors = ", ".join(paper.get("authors", []))

    doc = f"Title: {title}\nAuthors: {authors}\nAbstract: {abstract}"
    return clean_text(doc)


def dummy_embedding(text: str, dim: int = 384) -> np.ndarray:
    rng = np.random.default_rng(abs(hash(text)) % (2**32))
    return rng.standard_normal(dim)


def build_embeddings(docs: List[str]) -> np.ndarray:
    embeddings = []
    for doc in tqdm(docs, desc="Building embeddings"):
        emb = dummy_embedding(doc)
        embeddings.append(emb)
    return np.vstack(embeddings)


def main():
    # 1. 路径配置
    DATA_DIR = "data"
    OUTPUT_DIR = "outputs"
    PAPERS_PATH = os.path.join(DATA_DIR, "papers.json")
    REPORT_PATH = os.path.join(OUTPUT_DIR, "report.md")

    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 2. 加载或抓取论文
    print("检查/加载论文数据...")
    papers = load_or_fetch_papers(PAPERS_PATH, days=30, max_results=50)

    if not papers:
        print("没有可用论文数据，程序退出。")
        return

    # 按发布时间降序排序（新论文在前）
    papers.sort(
        key=lambda p: datetime.strptime(p.get("published", "1900-01-01"), "%a, %d %b %Y %H:%M:%S %Z") 
        if p.get("published") else datetime.min,
        reverse=True
    )

    # 3. 构建文档（用于 embeddings）
    print("Building documents...")
    documents = [build_document(paper) for paper in papers if build_document(paper)]
    print(f"生成 {len(documents)} 个有效文档")

    # 4. 生成 embeddings
    print("Generating embeddings...")
    embeddings = build_embeddings(documents)
    print("Embeddings shape:", embeddings.shape)

    # 5. 保存 embeddings
    np.save(os.path.join(OUTPUT_DIR, "embeddings.npy"), embeddings)

    # 6. 生成美观的 Markdown 报告（带链接）
    print("生成 Markdown 报告...")
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# UAV 相关论文追踪报告\n\n")
        f.write(f"**生成日期**: {date.today().strftime('%Y-%m-%d')}\n")
        f.write(f"**关键词**: {', '.join(ARXIV_CORE_KEYWORDS)}\n")
        f.write(f"**抓取范围**: 最近 30 天（可调整 days 参数）\n")
        f.write(f"**论文数量**: {len(papers)}\n\n")

        for i, paper in enumerate(papers, 1):
            title = clean_text(paper.get("title", "No title"))
            authors = ", ".join(paper.get("authors", []))
            abstract = clean_text(paper.get("abstract", "No abstract"))
            link = paper.get("link", "#")
            published = paper.get("published", "未知日期")

            f.write(f"## {i}. [{title}]({link})\n\n")
            f.write(f"**作者**: {authors}\n")
            f.write(f"**发布日期**: {published}\n")
            f.write(f"**arXiv 链接**: [{link}]({link})\n\n")
            f.write("**摘要**:\n")
            f.write(f"{abstract}\n\n")
            f.write("---\n\n")

    print(f"报告已保存到: {REPORT_PATH}")
    print("Pipeline 完成，结果已保存到 outputs/ 目录")


if __name__ == "__main__":
    main()
