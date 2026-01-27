# reporter/markdown.py
from datetime import date

def generate_markdown(papers):
    today = date.today().isoformat()
    md = f"# UAV Perception Papers – {today}\n\n"

    for p in papers:
        md += f"## {p['title']}\n"
        md += f"- **Authors**: {', '.join(p['authors'])}\n"
        md += f"- **Link**: {p['link']}\n"
        md += f"- **Fusion Type**: {p['fusion']}\n"
        md += f"- **Summary**:\n{p['abstract']}\n\n"

    return md
