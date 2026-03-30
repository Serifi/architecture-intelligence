import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


class LLMError(RuntimeError):
    pass


def generate_completion(prompt: str) -> str:
    if not GROQ_API_KEY:
        raise LLMError("GROQ_API_KEY ist nicht gesetzt.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "temperature": 0.0,
        "max_tokens": 1024,
        "response_format": {
            "type": "json_object"
        },
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert software architect. "
                    "You write high-quality Architecture Decision Records "
                    "based on given context and templates. "
                    "You MUST respond with a single valid JSON object only."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=90)
    except requests.RequestException as exc:
        raise LLMError(f"Groq request failed: {exc}") from exc

    if resp.status_code >= 400:
        raise LLMError(f"Groq API error {resp.status_code}: {resp.text}")

    try:
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as exc:
        raise LLMError(f"Unexpected Groq response format: {resp.text}") from exc
