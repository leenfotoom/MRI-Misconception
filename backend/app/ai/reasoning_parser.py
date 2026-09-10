from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx


LABELS = {
    "current_consumed": [
        "consume",
        "used up",
        "uses electricity",
        "less reaches",
        "weaker after",
    ],
    "proximity": [
        "closer",
        "nearer",
        "first bulb",
        "near battery",
        "closest",
    ],
    "constant_current": [
        "same current",
        "fixed current",
        "battery sends the same",
    ],
    "voltage_current_same": [
        "voltage is current",
        "volts are current",
        "same thing",
    ],
    "component_uses_all": [
        "uses all",
        "takes all",
        "nothing left",
    ],
    "sequential_arrival": [
        "reaches first",
        "gets there first",
        "before the second",
        "arrives first",
    ],
    "equal_parallel_split": [
        "splits equally",
        "fifty fifty",
        "equal current in parallel",
    ],
    "global_resistance": [
        "everywhere equally",
        "all current decreases",
        "same amount everywhere",
    ],
}


def heuristic_parse(
    reasoning: str,
    answer: str | None = None,
    misconceptions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    text = reasoning.lower().strip()
    labels: list[str] = []

    catalog = dict(LABELS)
    for misconception in misconceptions or []:
        claim = misconception.get("claim")
        if claim:
            catalog[claim] = [
                *misconception.get("keywords", []),
                *misconception.get("prototypes", []),
            ]

    for label, phrases in catalog.items():
        if any(phrase in text for phrase in phrases):
            labels.append(label)

    if re.search(r"(first|closer|near).*(battery|electricity)", text):
        if "proximity" not in labels:
            labels.append("proximity")

    if re.search(r"(electricity|current).*(first|before).*(second|later)", text):
        if "sequential_arrival" not in labels:
            labels.append("sequential_arrival")

    return {
        "prediction": answer,
        "claims": labels,
        "summary": reasoning.strip() or "No explanation provided.",
        "certainty": 0.72 if labels else 0.35,
        "parser": "heuristic_fallback",
    }


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"```$", "", text).strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("Model did not return valid JSON.")

    return json.loads(text[start : end + 1])


def cloudflare_parse(
    reasoning: str,
    answer: str | None = None,
    misconceptions: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    api_token = os.getenv("CLOUDFLARE_API_TOKEN")
    model = os.getenv("CLOUDFLARE_MODEL", "@cf/openai/gpt-oss-120b")

    if not account_id or not api_token:
        return None

    url = (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{account_id}/ai/v1/chat/completions"
    )

    dynamic_claims = [
        {
            "label": item["claim"],
            "meaning": item.get("description", item.get("short", "")),
        }
        for item in misconceptions or []
        if item.get("claim")
    ]
    allowed_labels = [item["label"] for item in dynamic_claims] or list(LABELS)

    system_prompt = f"""
You are a diagnostic reasoning parser for a STEM education system.

Your task is NOT to teach the student.
Do NOT correct the student.
Do NOT solve the STEM problem.

Analyze only the mental model behind the student's reasoning.

Allowed claim labels and meanings:
{json.dumps(dynamic_claims or allowed_labels, ensure_ascii=False)}

Return ONLY valid JSON in exactly this structure:
{{
  "prediction": "A",
  "claims": ["proximity"],
  "summary": "The student believes proximity to the battery increases power.",
  "certainty": 0.9
}}

Rules:
- prediction must be "A", "B", "same", or null
- claims may contain only labels from the allowed list
- certainty must be between 0 and 1
- summary must be short and neutral
- write summary in the same language used by the student
- do not explain the correct physics
- do not include markdown or extra text outside the JSON
"""

    user_prompt = f"""
Student prediction: {answer}

Student explanation:
{reasoning}
"""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 300,
    }

    try:
        response = httpx.post(
            url,
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()

        api_data = response.json()
        choices = api_data.get("choices", [])
        if not choices:
            raise ValueError(f"No choices returned: {api_data}")

        message = choices[0].get("message", {})
        model_output = message.get("content")
        if not model_output:
            raise ValueError(f"No content returned: {api_data}")

        data = _extract_json(model_output)
        valid_claims = [claim for claim in data.get("claims", []) if claim in allowed_labels]

        certainty = float(data.get("certainty", 0.5))
        certainty = max(0.0, min(1.0, certainty))

        prediction = data.get("prediction", answer)
        if prediction not in {"A", "B", "same", None}:
            prediction = answer

        return {
            "prediction": prediction,
            "claims": valid_claims,
            "summary": data.get("summary", reasoning.strip()),
            "certainty": certainty,
            "parser": "cloudflare_gpt_oss_120b",
        }

    except Exception as exc:
        print(
            "Cloudflare reasoning parser failed:",
            type(exc).__name__,
            str(exc),
        )
        return None


def parse_reasoning(
    reasoning: str,
    answer: str | None = None,
    misconceptions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return cloudflare_parse(reasoning, answer, misconceptions) or heuristic_parse(
        reasoning,
        answer,
        misconceptions,
    )
