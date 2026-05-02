from analyzer.hard_filter import hard_filter
from analyzer.quality_scorer import llm_review
from analyzer.aggregate import aggregate_score


def evaluate_paper(paper):
    ok, reason = hard_filter(paper)
    if not ok:
        return {
            "final_score": 0,
            "level": "Rejected",
            "confidence": "high",
            "reason": reason,
        }

    review = llm_review(paper["abstract"])
    if review is None:
        return {
            "final_score": 0,
            "level": "Passed",
            "confidence": "low",
            "reason": "Hard filter passed (LLM review skipped: no OPENAI_API_KEY)",
        }

    final_score, level = aggregate_score(review)
    return {
        "final_score": final_score,
        "level": level,
        "review": review,
        "confidence": review["confidence"],
        "reason": review["reason"],
    }
