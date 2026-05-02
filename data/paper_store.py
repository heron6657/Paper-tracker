import json
from pathlib import Path
from typing import List, Dict

DATA_PATH = Path("data/papers.json")


def load_paper_db(path: Path = DATA_PATH) -> List[Dict]:
    path = Path(path)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"{path} 格式错误，应为 list")
    return data


def save_paper_db(papers: List[Dict], path: Path = DATA_PATH) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)


def merge_papers(existing: List[Dict], new: List[Dict], key: str = "link") -> List[Dict]:
    """按 key 字段去重合并，已存在的保留旧版本（因为可能含评分结果）。"""
    seen = {p.get(key) for p in existing if p.get(key)}
    merged = list(existing)
    for p in new:
        if p.get(key) and p[key] not in seen:
            merged.append(p)
            seen.add(p[key])
    return merged
