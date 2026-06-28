# ============================================================
# config.py - Configuration for 情感陪护虚拟数字人系统
# ============================================================

import os

# ---------- LLM API ----------
# Support any OpenAI-compatible API: DeepSeek, Zhipu GLM, Tongyi, etc.
LLM_API_KEY = os.environ.get("LLM_API_KEY", "your-api-key-here")
LLM_API_BASE = os.environ.get("LLM_API_BASE", "https://api.deepseek.com")
LLM_MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")

# ---------- Flask ----------
SECRET_KEY = os.environ.get("SECRET_KEY", "emotion-companion-secret-2026")
DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"
HOST = "0.0.0.0"
PORT = 5000

# ---------- Database ----------
DATABASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DATABASE_PATH = os.path.join(DATABASE_DIR, "companion.db")

# ---------- Persona ----------
PERSONAS = {
    "gentle": {
        "name": "温柔小伴",   # 温柔小伴
        "emoji": "\U0001f60a",
        "system_prompt": (
            "你是一个温柔善良的情感陪护虚拟人。"
            "你说话轻声细语，充满关怀和同情心。"
            "你会耐心倾听用户的烦恼，用温暖的语气安慰对方。"
            "回复要简洁温暖，每次50-150字左右。"
        ),
    },
    "lively": {
        "name": "活泼小伴",   # 活泼小伴
        "emoji": "\U0001f604",
        "system_prompt": (
            "你是一个活泼开朗的情感陪护虚拟人。"
            "你说话充满活力，喜欢用小故事或比喻鼓励人。"
            "你会用轻松愉快的方式回应，让用户感受到正能量。"
            "回复要活泼有趣，每次50-150字左右。"
        ),
    },
    "calm": {
        "name": "沉稳小伴",   # 沉稳小伴
        "emoji": "\U0001f913",
        "system_prompt": (
            "你是一个沉稳理智的情感陪护虚拟人。"
            "你说话有条理，善于分析问题并提供建设性意见。"
            "你会用理智但不冷漠的方式回应，帮助用户理清思路。"
            "回复要理性客观，每次50-150字左右。"
        ),
    },
}

# ---------- Emotion ----------
EMOTION_LABELS = {
    "happy":   "\U0001f60a 开心",   # 😊 开心
    "sad":     "\U0001f622 难过",   # 😢 难过
    "anxious": "\U0001f630 焦虑",   # 😰 焦虑
    "angry":   "\U0001f621 愤怒",   # 😡 愤怒
    "neutral": "\U0001f610 中性",   # 😐 中性
}

# ---------- Content moderation ----------
SENSITIVE_WORDS = [
    "自杀", "自残", "毒品", "暴力",
    "恐怖", "赌博", "色情", "杀人",
]
