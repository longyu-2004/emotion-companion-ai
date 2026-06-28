# app.py
import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, Response, render_template, session, redirect, url_for
from config import PERSONA_PRESETS, EMOTION_TYPES
from database import init_db, get_or_create_default_user, get_user, update_user, \
    create_conversation, get_conversations, delete_conversation, \
    add_message, get_messages
from llm_service import detect_emotion, chat_completion
from moderator import check_content, sanitize_input

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
app.secret_key = "emotion-companion-secret-2026"


# ── JSON helper (compatible with old Flask) ───────────────────────────
def json_response(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False, default=str),
        status=status,
        mimetype="application/json",
    )


def get_json():
    """Safely parse request JSON body."""
    try:
        body = request.get_data(as_text=True)
        if not body:
            return {}
        return json.loads(body)
    except Exception:
        return {}


# ── Bootstrap ─────────────────────────────────────────────────────────
@app.before_request
def ensure_user():
    if "user_id" not in session:
        session["user_id"] = get_or_create_default_user()


# ── Pages ─────────────────────────────────────────────────────────────
@app.route("/")
def index():
    user = get_user(session["user_id"])
    conversations = get_conversations(session["user_id"])
    return render_template("index.html", user=user, conversations=conversations,
                           personas=PERSONA_PRESETS, emotion_types=EMOTION_TYPES)


# ── API: Settings ─────────────────────────────────────────────────────
@app.route("/api/settings", methods=["GET"])
def get_settings():
    user = get_user(session["user_id"])
    return json_response({"ok": True, "user": user,
                          "personas": {k: {"name": v["name"]} for k, v in PERSONA_PRESETS.items()}})


@app.route("/api/settings", methods=["POST"])
def update_settings():
    data = get_json()
    nickname = (data.get("nickname") or "").strip()
    persona = (data.get("persona") or "").strip()
    if persona and persona not in PERSONA_PRESETS:
        return json_response({"ok": False, "error": "Invalid persona"}, 400)
    update_user(session["user_id"],
                nickname=nickname or None,
                persona=persona or None)
    return json_response({"ok": True})


# ── API: Conversations ────────────────────────────────────────────────
@app.route("/api/conversations", methods=["GET"])
def list_conversations():
    convs = get_conversations(session["user_id"])
    return json_response({"ok": True, "conversations": convs})


@app.route("/api/conversations", methods=["POST"])
def new_conversation():
    cid = create_conversation(session["user_id"])
    return json_response({"ok": True, "id": cid})


@app.route("/api/conversations/<cid>", methods=["DELETE"])
def remove_conversation(cid):
    delete_conversation(cid)
    return json_response({"ok": True})


# ── API: Messages ─────────────────────────────────────────────────────
@app.route("/api/conversations/<cid>/messages", methods=["GET"])
def list_messages(cid):
    msgs = get_messages(cid)
    return json_response({"ok": True, "messages": msgs})


# ── API: Emotion Statistics ───────────────────────────────────────────
@app.route("/api/stats", methods=["GET"])
def emotion_stats():
    import sqlite3
    conn = sqlite3.connect(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "app", "data", "companion.db"
    ))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT emotion, COUNT(*) as cnt FROM messages "
        "WHERE role='assistant' GROUP BY emotion"
    ).fetchall()
    conn.close()
    stats = {r["emotion"]: r["cnt"] for r in rows}
    total = sum(stats.values()) or 1
    return json_response({
        "ok": True,
        "stats": stats,
        "total": total,
        "percentages": {k: round(v / total * 100, 1) for k, v in stats.items()},
    })


# ── API: Export Conversation ──────────────────────────────────────────
@app.route("/api/conversations/<cid>/export", methods=["GET"])
def export_conversation(cid):
    msgs = get_messages(cid)
    lines = []
    lines.append("=" * 50)
    lines.append("  情感陪护虚拟数字人 - 对话记录导出")
    lines.append("=" * 50)
    lines.append("")
    for m in msgs:
        role_label = "我" if m["role"] == "user" else "小伴"
        emotion_tag = f" [{m.get('emotion', '')}]" if m["role"] == "assistant" else ""
        lines.append(f"[{m.get('created_at', '')}] {role_label}{emotion_tag}:")
        lines.append(f"  {m['content']}")
        lines.append("")
    lines.append("=" * 50)
    lines.append("  感谢您的使用，祝您心情愉快！")
    lines.append("=" * 50)
    text = "\n".join(lines)
    return Response(
        text,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment; filename=conversation_{cid}.txt"},
    )


# ── API: Chat ─────────────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def chat():
    data = get_json()
    user_input = (data.get("message") or "").strip()
    conversation_id = data.get("conversation_id")

    if not user_input:
        return json_response({"ok": False, "error": "Empty message"}, 400)

    # Sanitize
    user_input = sanitize_input(user_input)

    # Content moderation
    mod_result = check_content(user_input)
    if mod_result["flagged"]:
        # Check for crisis keywords - provide guidance instead of just blocking
        crisis_guidance = None
        for kw in mod_result["matches"]:
            from moderator import CRISIS_GUIDANCE
            for crisis_kw, guidance in CRISIS_GUIDANCE.items():
                if crisis_kw in kw:
                    crisis_guidance = guidance
                    break
        if crisis_guidance:
            # Save the user message and respond with care
            if not conversation_id:
                conversation_id = create_conversation(session["user_id"])
            add_message(conversation_id, "user", user_input)
            add_message(conversation_id, "assistant", crisis_guidance, emotion="anxious")
            return json_response({
                "ok": True,
                "reply": crisis_guidance,
                "emotion": "anxious",
                "conversation_id": conversation_id,
            })
        return json_response({
            "ok": False,
            "error": "您的消息包含敏感内容，请重新表述。",
            "matches": mod_result["matches"],
        }, 400)

    # Get user persona
    user = get_user(session["user_id"])
    persona_key = user["persona"] if user else "gentle"

    # Auto-create conversation if needed
    if not conversation_id:
        conversation_id = create_conversation(session["user_id"])

    # Save user message
    add_message(conversation_id, "user", user_input)

    # Detect emotion
    emotion = detect_emotion(user_input)

    # Build context (last 10 messages for multi-turn)
    history = get_messages(conversation_id)
    context = []
    for m in history[-10:]:
        context.append({"role": m["role"], "content": m["content"]})

    # Call LLM
    try:
        reply = chat_completion(context, persona_key=persona_key)
    except Exception as e:
        print(f"[LLM ERROR] {e}")
        reply = f"抱歉，我暂时无法回应，请稍后再试。\n\n[调试信息] {e}"

    # Moderation on reply
    reply_mod = check_content(reply)
    if reply_mod["flagged"]:
        reply = reply_mod["filtered_text"]

    # Save assistant message
    add_message(conversation_id, "assistant", reply, emotion=emotion)

    return json_response({
        "ok": True,
        "reply": reply,
        "emotion": emotion,
        "conversation_id": conversation_id,
    })


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("=" * 50)
    print("  Emotion Companion AI System")
    print("  http://127.0.0.1:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
