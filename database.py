# database.py
import sqlite3
import os
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "data", "companion.db")


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id          TEXT PRIMARY KEY,
        nickname    TEXT DEFAULT '同学',
        persona     TEXT DEFAULT 'gentle',
        created_at  TEXT DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS conversations (
        id              TEXT PRIMARY KEY,
        user_id         TEXT NOT NULL,
        title           TEXT DEFAULT '新对话',
        created_at      TEXT DEFAULT (datetime('now','localtime')),
        updated_at      TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS messages (
        id              TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL,
        role            TEXT NOT NULL CHECK(role IN ('user','assistant')),
        content         TEXT NOT NULL,
        emotion         TEXT DEFAULT 'neutral',
        created_at      TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
    );
    """)
    conn.commit()
    conn.close()


def create_user(nickname="同学", persona="gentle"):
    conn = get_db()
    uid = str(uuid.uuid4())[:8]
    conn.execute("INSERT INTO users (id,nickname,persona) VALUES (?,?,?)", (uid, nickname, persona))
    conn.commit()
    conn.close()
    return uid


def get_or_create_default_user():
    conn = get_db()
    row = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
    if row:
        conn.close()
        return row["id"]
    conn.close()
    return create_user()


def get_user(uid):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_user(uid, nickname=None, persona=None):
    conn = get_db()
    if nickname:
        conn.execute("UPDATE users SET nickname=? WHERE id=?", (nickname, uid))
    if persona:
        conn.execute("UPDATE users SET persona=? WHERE id=?", (persona, uid))
    conn.commit()
    conn.close()


def create_conversation(user_id, title="新对话"):
    conn = get_db()
    cid = str(uuid.uuid4())[:8]
    conn.execute("INSERT INTO conversations (id,user_id,title) VALUES (?,?,?)",
                 (cid, user_id, title))
    conn.commit()
    conn.close()
    return cid


def get_conversations(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM conversations WHERE user_id=? ORDER BY updated_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_conversation(cid):
    conn = get_db()
    conn.execute("DELETE FROM messages WHERE conversation_id=?", (cid,))
    conn.execute("DELETE FROM conversations WHERE id=?", (cid,))
    conn.commit()
    conn.close()


def add_message(conversation_id, role, content, emotion="neutral"):
    conn = get_db()
    mid = str(uuid.uuid4())[:8]
    conn.execute(
        "INSERT INTO messages (id,conversation_id,role,content,emotion) VALUES (?,?,?,?,?)",
        (mid, conversation_id, role, content, emotion)
    )
    if role == "user":
        conn.execute(
            "UPDATE conversations SET updated_at=datetime('now','localtime'), "
            "title=CASE WHEN title='新对话' THEN substr(?,1,20) ELSE title END WHERE id=?",
            (content, conversation_id)
        )
    else:
        conn.execute(
            "UPDATE conversations SET updated_at=datetime('now','localtime') WHERE id=?",
            (conversation_id,)
        )
    conn.commit()
    conn.close()
    return mid


def get_messages(conversation_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM messages WHERE conversation_id=? ORDER BY created_at ASC",
        (conversation_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
