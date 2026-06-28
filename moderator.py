# moderator.py
import re
from config import SENSITIVE_WORDS

# Crisis keywords with caring guidance responses
CRISIS_GUIDANCE = {
    "自杀": (
        "我很担心你现在的感受。如果你正在经历困难的时刻，请知道你并不孤单。\n\n"
        "我作为AI无法提供专业帮助，但我真心建议你：\n"
        "拨打全国心理援助热线：400-161-9995\n"
        "或联系学校心理咨询中心，那里有专业的老师可以帮助你。\n\n"
        "你的感受很重要，也有人愿意倾听和帮助你。请照顾好自己。"
    ),
    "自残": (
        "听到你这样说，我很担心你。伤害自己并不能真正解决问题。\n\n"
        "我建议你联系：\n"
        "全国心理援助热线：400-161-9995\n"
        "或找你信任的人聊一聊，比如朋友、家人或学校的心理老师。\n\n"
        "你值得被关心和帮助，请给自己一个机会。"
    ),
    "毒品": (
        "毒品对身心健康有严重危害，我不能提供任何相关信息。\n\n"
        "如果你或身边的人遇到相关困扰，建议联系：\n"
        "全国禁毒热线：12345\n"
        "或向学校辅导员寻求帮助。\n\n"
        "请珍惜自己的健康和未来。"
    ),
    "暴力": (
        "我无法提供任何与暴力相关的内容。\n\n"
        "如果你正面临暴力威胁，请立即拨打110报警。\n"
        "或联系学校保卫处、辅导员寻求保护和帮助。\n\n"
        "你的安全是最重要的。"
    ),
    "赌博": (
        "赌博不仅违法，还会给个人和家庭带来严重伤害。\n\n"
        "如果你正在经历这方面的困扰，建议：\n"
        "联系学校心理咨询中心获取专业帮助\n"
        "或拨打全国心理援助热线：400-161-9995\n\n"
        "远离赌博，珍惜生活。"
    ),
}


def check_content(text: str) -> dict:
    """
    Check text for sensitive words.
    Returns: {"flagged": bool, "filtered_text": str, "matches": list}
    """
    matches = []
    filtered = text
    for word in SENSITIVE_WORDS:
        if word in text:
            matches.append(word)
            filtered = filtered.replace(word, "***")
    return {
        "flagged": len(matches) > 0,
        "filtered_text": filtered,
        "matches": matches,
    }


def sanitize_input(text: str) -> str:
    """Basic XSS and injection sanitization for user input."""
    text = re.sub(r"<[^>]+>", "", text)      # Strip HTML tags
    text = text.replace("\x00", "")            # Remove null bytes
    return text[:500]                          # Enforce max length
