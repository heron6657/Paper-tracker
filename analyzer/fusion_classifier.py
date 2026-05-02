import os
import json

PROMPT = """
You are an expert in multimodal perception for UAVs.

Given the following abstract, classify the sensor fusion strategy:
- Early Fusion
- Intermediate Fusion
- Late Fusion
- No Fusion

Return JSON only in this format:
{"fusion_type": "<one of the four types above>"}

Abstract:
"""


def classify_fusion(abstract: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Unknown"

    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a research assistant."},
            {"role": "user", "content": PROMPT + abstract}
        ],
        temperature=0
    )

    try:
        result = json.loads(response.choices[0].message.content)
        return result.get("fusion_type", "Unknown")
    except json.JSONDecodeError:
        return response.choices[0].message.content.strip()
