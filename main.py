import json
import os
from typing import List, Dict

import numpy as np
from tqdm import tqdm
from datetime import date

from crawler.arxiv import fetch_arxiv_papers
from analyzer.quality_pipeline import evaluate_paper
from reporter.markdown import generate_markdown
from data.paper_store import load_paper_db, save_paper_db


from config import QUALITY_LEVEL_KEEP

from crawler.arxiv import fetch_arxiv_papers
from crawler.keywords import ARXIV_CORE_KEYWORDS

papers = fetch_arxiv_papers(
    keywords=ARXIV_CORE_KEYWORDS,
    days=7,
    max_results=20
)




def load_papers(json_path: str) -> List[Dict]:
    """
    读取 papers.json
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"{json_path} 不存在")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("papers.json 格式错误，最外层应为 list")

    return data


def clean_text(text: str) -> str:
    
    if text is None:
        return ""

    text = text.replace("\n", " ").replace("\t", " ")
    text = " ".join(text.split())
    return text.strip()


def build_document(paper: Dict) -> str:
   
    title = clean_text(paper.get("title", ""))
    abstract = clean_text(paper.get("abstract", ""))
    authors = ", ".join(paper.get("authors", []))

    doc = f"""
    Title: {title}
    Authors: {authors}
    Abstract: {abstract}
    """
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
    PAPERS_PATH = os.path.join(DATA_DIR, "papers.json")

    # 2. 加载论文数据
    print(" Loading papers...")
    papers = load_papers(PAPERS_PATH)
    print(f" 共加载 {len(papers)} 篇论文")

    # 3. 构建文档
    print(" Building documents...")
    documents = []
    for paper in papers:
        doc = build_document(paper)
        if doc:
            documents.append(doc)

    print(f" 生成 {len(documents)} 个文档")

    
    print(" Generating embeddings...")
    embeddings = build_embeddings(documents)

    print(" Embeddings shape:", embeddings.shape)

    
    os.makedirs("outputs", exist_ok=True)
    np.save("outputs/embeddings.npy", embeddings)

    with open("outputs/documents.txt", "w", encoding="utf-8") as f:
        for doc in documents:
            f.write(doc + "\n\n")

    print("🎉 Pipeline 完成，结果已保存到 outputs/ 目录")




if __name__ == "__main__":
    main()
