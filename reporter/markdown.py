from datetime import date
from typing import List, Dict


def _clean(text):
    if not text:
        return ""
    return " ".join(str(text).replace("\n", " ").replace("\t", " ").split()).strip()


def generate_markdown(papers: List[Dict], keywords: List[str] = None, days: int = None) -> str:
    today = date.today().isoformat()
    lines = [f"# UAV 相关论文追踪报告 – {today}\n"]

    if keywords:
        lines.append(f"**关键词**: {', '.join(keywords)}  ")
    if days is not None:
        lines.append(f"**抓取范围**: 最近 {days} 天  ")
    lines.append(f"**论文数量**: {len(papers)}\n")

    for i, p in enumerate(papers, 1):
        title = _clean(p.get("title", "No title"))
        authors = ", ".join(p.get("authors", []))
        abstract = _clean(p.get("abstract", "No abstract"))
        link = p.get("link", "#")
        published = p.get("published", "未知日期")
        fusion = p.get("fusion", "")
        quality = p.get("quality") or {}
        level = quality.get("level", "")
        score = quality.get("final_score", "")
        reason = quality.get("reason", "")

        lines.append(f"## {i}. [{title}]({link})\n")
        lines.append(f"- **作者**: {authors}")
        lines.append(f"- **发布日期**: {published}")
        lines.append(f"- **arXiv 链接**: {link}")
        if level:
            lines.append(f"- **质量等级**: {level}（score={score}）")
        if fusion:
            lines.append(f"- **融合类型**: {fusion}")
        if reason:
            lines.append(f"- **评审理由**: {reason}")
        lines.append("")
        lines.append("**摘要**:\n")
        lines.append(abstract)
        lines.append("\n---\n")

    return "\n".join(lines)
