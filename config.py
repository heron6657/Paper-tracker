import os

# arXiv search
ARXIV_DAYS = 7
MAX_RESULTS = 50

# Quality control
# Levels: "High-quality", "Medium-quality", "Low-quality", "Passed", "Rejected"
# "Passed" 表示通过硬过滤但未做 LLM 评审（无 OPENAI_API_KEY 时使用）
QUALITY_LEVEL_KEEP = ["High-quality", "Medium-quality", "Passed"]

# Paths
DATA_DIR = "data"
OUTPUT_DIR = "outputs"
PAPERS_PATH = os.path.join(DATA_DIR, "papers.json")
REPORT_PATH = os.path.join(OUTPUT_DIR, "report.md")
EMBEDDINGS_PATH = os.path.join(OUTPUT_DIR, "embeddings.npy")

# Feature toggles
ENABLE_FUSION_CLASSIFY = True   # 需要 OPENAI_API_KEY，否则会返回 "Unknown"
ENABLE_EMBEDDINGS = False       # 当前为 dummy 实现，默认关闭
