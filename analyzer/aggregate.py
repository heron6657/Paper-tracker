def aggregate_score(review):
    score = (
        review["novelty"] * 0.3 +
        review["method"] * 0.3 +
        review["experiment"] * 0.2 +
        review["relevance"] * 0.2
    )

    if score >= 4.2:
        level = "High-quality"
    elif score >= 3.5:
        level = "Medium-quality"
    else:
        level = "Low-quality"

    return round(score, 2), level
