QUALITY_PROMPT = """
You are a senior reviewer for top-tier robotics and vision conferences
(e.g., CVPR, ICCV, ICRA).

Evaluate the following abstract and score it from 1 (very weak) to 5 (excellent)
on these criteria:

1. Technical novelty
2. Method completeness (clear pipeline, not a toy example)
3. Experimental sufficiency
4. Relevance to UAV perception

Return JSON only in this format:
{
  "novelty": 1-5,
  "method": 1-5,
  "experiment": 1-5,
  "relevance": 1-5,
  "overall": 1-5,
  "confidence": "low/medium/high",
  "reason": "one concise sentence"
}

Abstract:
"""

import os
import json


def llm_review(abstract: str):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a strict academic reviewer."},
            {"role": "user", "content": QUALITY_PROMPT + abstract}
        ],
        temperature=0
    )

    content = response.choices[0].message.content
    return json.loads(content)
