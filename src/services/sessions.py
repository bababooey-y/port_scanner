import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, redirect, url_for
from src.db import get_db

SESSION_LIFETIME = timedelta(minutes=1440)


def generate_session_id():
    """
    Génère un identifiant de session sécurisé.
    secrets.token_hex génère une chaîne aléatoire cryptographiquement sûre.
    """
    return secrets.token_hex(32)  # 64 caractères hexadécimaux


def create_session(user_id: str) -> str:
    session_id = generate_session_id()
    created_at = datetime.now()
    expires_at = created_at + SESSION_LIFETIME

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO sessions (session_id, user_id, created_at, expires_at)
        VALUES (?, ?, ?, ?)
        """,
        (session_id, user_id, created_at.isoformat(), expires_at.isoformat()),
    )
    conn.commit()
    conn.close()

    return session_id


def get_session(session_id: str) -> dict | None:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT session_id, user_id, created_at, expires_at FROM sessions WHERE session_id = ?",
        (session_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    expires_at = datetime.fromisoformat(row["expires_at"])

    if datetime.now() > expires_at:
        delete_session(session_id)
        return None

    return {
        "session_id": row["session_id"],
        "user_id": row["user_id"],
        "created_at": datetime.fromisoformat(row["created_at"]),
        "expires_at": expires_at,
    }


def delete_session(session_id: str) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def get_current_user(request) -> str | None:
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None

    session = get_session(session_id)
    if not session:
        return None

    return session["user_id"]


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user(request)
        if not current_user:
            return redirect(url_for("auth.get_login"))
        return f(*args, **kwargs)
    return decorated_function
