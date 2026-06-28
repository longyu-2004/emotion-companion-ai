# llm_service.py
import requests
import json
import re
from config import LLM_API_KEY, LLM_API_BASE, LLM_MODEL, PERSONA_PRESETS, EMOTION_TYPES


# ── Emotion detection via prompt engineering ──────────────────────────
EMOTION_DETECT_PROMPT = """你是一个情感识别专家。请分析用户输入的情感，只返回以下标签之一：
happy, sad, anxious, angry, neutral

判断标准：
- 开心、高兴、兴奋、满意、感动 → happy
- 难过、伤心、失落、沮丧、孤独、哭 → sad
- 焦虑、紧张、担心、不安、害怕、压力 → anxious
- 愤怒、生气、不满、烦躁、讨厌 → angry
- 以上都不是、陈述事实、普通对话 → neutral

用户输入：{user_input}

只返回标签，不要任何解释："""


def detect_emotion(user_input: str) -> str:
    """Call LLM to detect user emotion, return one of EMOTION_TYPES."""
    try:
        prompt = EMOTION_DETECT_PROMPT.format(user_input=user_input)
        resp = _call_llm_raw([
            {"role": "system", "content": "你是一个情感识别助手，只输出情感标签。"},
            {"role": "user", "content": prompt},
        ], temperature=0.1, max_tokens=10)
        # Extract label from response
        resp_clean = resp.strip().lower()
        for emo in EMOTION_TYPES:
            if emo in resp_clean:
                return emo
        return "neutral"
    except Exception:
        # Fallback: keyword matching
        return _fallback_emotion(user_input)


def _fallback_emotion(text: str) -> str:
    """Simple keyword-based fallback when API is unavailable."""
    happy_kw = ["开心", "高兴", "兴奋", "满意", "感动", "快乐", "哈哈", "太好了"]
    sad_kw = ["难过", "伤心", "失落", "沮丧", "孤独", "哭", "痛苦", "难受", "唉"]
    anxious_kw = ["焦虑", "紧张", "担心", "不安", "害怕", "压力", "忐忑", "慌"]
    angry_kw = ["愤怒", "生气", "不满", "烦躁", "讨厌", "气死", "烦死了"]
    for kw in happy_kw:
        if kw in text:
            return "happy"
    for kw in sad_kw:
        if kw in text:
            return "sad"
    for kw in anxious_kw:
        if kw in text:
            return "anxious"
    for kw in angry_kw:
        if kw in text:
            return "angry"
    return "neutral"


# ── Chat completion ───────────────────────────────────────────────────
def chat_completion(messages: list, persona_key: str = "gentle",
                    temperature: float = 0.7, max_tokens: int = 500) -> str:
    """Generate a chat reply using the LLM with persona system prompt."""
    persona = PERSONA_PRESETS.get(persona_key, PERSONA_PRESETS["gentle"])
    system_msg = {
        "role": "system",
        "content": persona["system_prompt"],
    }
    full_messages = [system_msg] + messages
    return _call_llm_raw(full_messages, temperature=temperature, max_tokens=max_tokens)


def _call_llm_raw(messages: list, temperature: float = 0.7,
                  max_tokens: int = 500) -> str:
    """Raw call to OpenAI-compatible chat completion API."""
    url = f"{LLM_API_BASE.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}",
    }
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except requests.exceptions.HTTPError as e:
        body = e.response.text if e.response is not None else "no response"
        raise Exception(f"HTTP {e.response.status_code}: {body[:300]}") from e
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"Connection failed: {url}") from e
    except requests.exceptions.Timeout:
        raise Exception("Request timed out (30s)") from None
    except (KeyError, IndexError) as e:
        raise Exception(f"Unexpected response format: {e}") from e
