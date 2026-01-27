# analyzer/fusion_classifier.py
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

PROMPT = """
You are an expert in multimodal perception for UAVs.

Given the following abstract, classify the sensor fusion strategy:
- Early Fusion
- Intermediate Fusion
- Late Fusion
- No Fusion

Return JSON only.

Abstract:
"""

def classify_fusion(abstract: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 或国产模型
        messages=[
            {"role": "system", "content": "You are a research assistant."},
            {"role": "user", "content": PROMPT + abstract}
        ],
        temperature=0
    )

    return response.choices[0].message.content

