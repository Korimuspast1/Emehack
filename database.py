"""
Database Module - SQLite Persistence for Pax Historia Bot
"""
import sqlite3
import json
import os
import time
from typing import Dict, List, Optional, Any
from config import DATABASE_PATH, AI_PROVIDER_BUILTIN, DEFAULT_MODELS

def get_db_connection():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        language TEXT DEFAULT 'ru',
        active_game_id TEXT,
        ai_provider TEXT DEFAULT 'builtin',
        ai_model TEXT,
        ai_api_key TEXT,
        ai_endpoint TEXT,
        ai_temperature REAL DEFAULT 0.7,
        created_at INTEGER
    )
    """)

    # Games Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS games (
        game_id TEXT PRIMARY KEY,
        user_id INTEGER,
        title TEXT,
        preset_id TEXT,
        current_year INTEGER,
        current_month INTEGER,
        current_day INTEGER,
        player_nation TEXT,
        difficulty TEXT DEFAULT 'normal',
        turn_count INTEGER DEFAULT 0,
        state_json TEXT,
        history_json TEXT,
        created_at INTEGER,
        updated_at INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """)

    # Saves Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saves (
        save_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        game_id TEXT,
        slot_name TEXT,
        year INTEGER,
        month INTEGER,
        day INTEGER,
        player_nation TEXT,
        state_json TEXT,
        history_json TEXT,
        created_at INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """)

    # Custom Prompts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS custom_prompts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        prompt_key TEXT,
        prompt_text TEXT,
        is_active INTEGER DEFAULT 1,
        updated_at INTEGER,
        UNIQUE(user_id, prompt_key)
    )
    """)

    # Custom Scenarios Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS custom_scenarios (
        scenario_id TEXT PRIMARY KEY,
        user_id INTEGER,
        title TEXT,
        description TEXT,
        start_year INTEGER,
        start_month INTEGER,
        start_day INTEGER DEFAULT 1,
        nations_json TEXT,
        events_json TEXT,
        map_json TEXT,
        is_public INTEGER DEFAULT 0,
        created_at INTEGER
    )
    """)

    # Rewind History Table (last 10 turns per game)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rewind_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id TEXT,
        turn_number INTEGER,
        year INTEGER,
        month INTEGER,
        day INTEGER,
        state_json TEXT,
        created_at INTEGER
    )
    """)

    conn.commit()
    conn.close()

# Initialize immediately
init_db()

# --- User Operations ---
def get_or_create_user(user_id: int, username: Optional[str] = None) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    now = int(time.time())
    if not row:
        default_model = DEFAULT_MODELS[AI_PROVIDER_BUILTIN]
        cursor.execute("""
        INSERT INTO users (user_id, username, language, active_game_id, ai_provider, ai_model, ai_api_key, ai_endpoint, ai_temperature, created_at)
        VALUES (?, ?, 'ru', NULL, 'builtin', ?, NULL, NULL, 0.7, ?)
        """, (user_id, username or "User", default_model, now))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
    elif username and row["username"] != username:
        cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, user_id))
        conn.commit()
    user_dict = dict(row)
    conn.close()
    return user_dict

def update_user_settings(user_id: int, **kwargs) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    fields = []
    values = []
    for k, v in kwargs.items():
        fields.append(f"{k} = ?")
        values.append(v)
    if not fields:
        conn.close()
        return False
    values.append(user_id)
    cursor.execute(f"UPDATE users SET {', '.join(fields)} WHERE user_id = ?", tuple(values))
    conn.commit()
    conn.close()
    return True

# --- Game Operations ---
def save_or_update_game(game_id: str, user_id: int, title: str, preset_id: str,
                        year: int, month: int, day: int, player_nation: str,
                        difficulty: str, turn_count: int, state: Dict[str, Any],
                        history: List[Dict[str, Any]]) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = int(time.time())
    state_json = json.dumps(state, ensure_ascii=False)
    history_json = json.dumps(history, ensure_ascii=False)

    cursor.execute("SELECT game_id FROM games WHERE game_id = ?", (game_id,))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("""
        UPDATE games SET title = ?, current_year = ?, current_month = ?, current_day = ?,
        player_nation = ?, difficulty = ?, turn_count = ?, state_json = ?, history_json = ?, updated_at = ?
        WHERE game_id = ?
        """, (title, year, month, day, player_nation, difficulty, turn_count, state_json, history_json, now, game_id))
    else:
        cursor.execute("""
        INSERT INTO games (game_id, user_id, title, preset_id, current_year, current_month, current_day,
        player_nation, difficulty, turn_count, state_json, history_json, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (game_id, user_id, title, preset_id, year, month, day, player_nation, difficulty, turn_count, state_json, history_json, now, now))

    # Also update user active game
    cursor.execute("UPDATE users SET active_game_id = ? WHERE user_id = ?", (game_id, user_id))

    # Save rewind snapshot
    cursor.execute("""
    INSERT INTO rewind_history (game_id, turn_number, year, month, day, state_json, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (game_id, turn_count, year, month, day, state_json, now))

    # Prune rewind history to max 15 snapshots
    cursor.execute("""
    DELETE FROM rewind_history WHERE id NOT IN (
        SELECT id FROM rewind_history WHERE game_id = ? ORDER BY id DESC LIMIT 15
    ) AND game_id = ?
    """, (game_id, game_id))

    conn.commit()
    conn.close()
    return True

def get_game(game_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM games WHERE game_id = ?", (game_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["state"] = json.loads(d["state_json"]) if d["state_json"] else {}
    d["history"] = json.loads(d["history_json"]) if d["history_json"] else []
    return d

def get_user_games(user_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM games WHERE user_id = ? ORDER BY updated_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for row in rows:
        d = dict(row)
        d["state"] = json.loads(d["state_json"]) if d["state_json"] else {}
        d["history"] = json.loads(d["history_json"]) if d["history_json"] else []
        results.append(d)
    return results

def get_rewind_snapshots(game_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rewind_history WHERE game_id = ? ORDER BY turn_number DESC", (game_id,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        d["state"] = json.loads(d["state_json"]) if d["state_json"] else {}
        results.append(d)
    return results

# --- Save Slots ---
def create_save_slot(user_id: int, game_id: str, slot_name: str, year: int, month: int, day: int,
                     player_nation: str, state: Dict[str, Any], history: List[Dict[str, Any]]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = int(time.time())
    state_json = json.dumps(state, ensure_ascii=False)
    history_json = json.dumps(history, ensure_ascii=False)

    cursor.execute("""
    INSERT INTO saves (user_id, game_id, slot_name, year, month, day, player_nation, state_json, history_json, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, game_id, slot_name, year, month, day, player_nation, state_json, history_json, now))
    save_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return save_id

def get_user_saves(user_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM saves WHERE user_id = ? ORDER BY created_at DESC LIMIT 20", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        d["state"] = json.loads(d["state_json"]) if d["state_json"] else {}
        d["history"] = json.loads(d["history_json"]) if d["history_json"] else []
        results.append(d)
    return results

def get_save_by_id(save_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM saves WHERE save_id = ?", (save_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["state"] = json.loads(d["state_json"]) if d["state_json"] else {}
    d["history"] = json.loads(d["history_json"]) if d["history_json"] else []
    return d

def delete_save_by_id(save_id: int, user_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saves WHERE save_id = ? AND user_id = ?", (save_id, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

# --- Custom Prompts ---
def get_user_custom_prompts(user_id: int) -> Dict[str, str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT prompt_key, prompt_text FROM custom_prompts WHERE user_id = ? AND is_active = 1", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return {row["prompt_key"]: row["prompt_text"] for row in rows}

def set_user_custom_prompt(user_id: int, prompt_key: str, prompt_text: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = int(time.time())
    cursor.execute("""
    INSERT INTO custom_prompts (user_id, prompt_key, prompt_text, is_active, updated_at)
    VALUES (?, ?, ?, 1, ?)
    ON CONFLICT(user_id, prompt_key) DO UPDATE SET
    prompt_text = excluded.prompt_text,
    is_active = 1,
    updated_at = excluded.updated_at
    """, (user_id, prompt_key, prompt_text, now))
    conn.commit()
    conn.close()
    return True

def reset_user_custom_prompt(user_id: int, prompt_key: Optional[str] = None) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    if prompt_key:
        cursor.execute("DELETE FROM custom_prompts WHERE user_id = ? AND prompt_key = ?", (user_id, prompt_key))
    else:
        cursor.execute("DELETE FROM custom_prompts WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True

# --- Custom Scenarios ---
def save_custom_scenario(scenario_id: str, user_id: int, title: str, description: str,
                         start_year: int, start_month: int, nations: List[Dict[str, Any]],
                         events: List[Dict[str, Any]], map_data: Dict[str, Any], is_public: bool = False) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    now = int(time.time())
    cursor.execute("""
    INSERT INTO custom_scenarios (scenario_id, user_id, title, description, start_year, start_month, nations_json, events_json, map_json, is_public, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(scenario_id) DO UPDATE SET
    title = excluded.title,
    description = excluded.description,
    start_year = excluded.start_year,
    start_month = excluded.start_month,
    nations_json = excluded.nations_json,
    events_json = excluded.events_json,
    map_json = excluded.map_json,
    is_public = excluded.is_public
    """, (
        scenario_id, user_id, title, description, start_year, start_month,
        json.dumps(nations, ensure_ascii=False),
        json.dumps(events, ensure_ascii=False),
        json.dumps(map_data, ensure_ascii=False),
        1 if is_public else 0,
        now
    ))
    conn.commit()
    conn.close()
    return True

def get_custom_scenarios(user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT * FROM custom_scenarios WHERE user_id = ? OR is_public = 1 ORDER BY created_at DESC", (user_id,))
    else:
        cursor.execute("SELECT * FROM custom_scenarios WHERE is_public = 1 ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    scenarios = []
    for r in rows:
        d = dict(r)
        d["nations"] = json.loads(d["nations_json"]) if d["nations_json"] else []
        d["events"] = json.loads(d["events_json"]) if d["events_json"] else []
        d["map_data"] = json.loads(d["map_json"]) if d["map_json"] else {}
        scenarios.append(d)
    return scenarios

def get_custom_scenario_by_id(scenario_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM custom_scenarios WHERE scenario_id = ?", (scenario_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["nations"] = json.loads(d["nations_json"]) if d["nations_json"] else []
    d["events"] = json.loads(d["events_json"]) if d["events_json"] else []
    d["map_data"] = json.loads(d["map_json"]) if d["map_json"] else {}
    return d
