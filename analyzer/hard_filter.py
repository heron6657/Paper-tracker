def hard_filter(paper):
    abstract = paper["abstract"].lower()

    #  字数过滤
    if len(abstract.split()) < 120:
        return False, "Abstract too short"

    #  关键科研结构词
    structure_words = [
        "we propose", "framework", "pipeline",
        "experiments", "results", "evaluation"
    ]
    if not any(w in abstract for w in structure_words):
        return False, "Lack of research structure"

    #  UAV / Perception 相关性
    relevance_words = ["uav", "drone", "aerial", "lidar", "camera"]
    if not any(w in abstract for w in relevance_words):
        return False, "Low relevance"

    return True, "Pass"
