"""
Core Game Engine for Pax Historia (2026 Engine)
Handles Game Loop, Decisional Pause, Auto-Time-Skip, Unscripted Emergent Sandbox,
Country Granular Stats Viewing & Modifying, Rewind, Saves, and AI Integration.
"""
import copy
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple

import database
from config import DEFAULT_SCENARIO_ID, DEFAULT_YEAR, DEFAULT_MONTH, DEFAULT_DAY, TIME_STEPS
from game.presets import get_preset_by_id, get_all_presets
from game.state import GameSession, CountryState
from game.actions_registry import get_action_by_id, get_all_actions
from ai.engine import AIEngine

# Active in-memory session cache for instant responsiveness
_SESSIONS_CACHE: Dict[str, GameSession] = {}

def get_or_load_session(user_id: int) -> GameSession:
    """Retrieves current user game session from cache or database."""
    user = database.get_or_create_user(user_id)
    active_gid = user.get("active_game_id")
    
    if active_gid and active_gid in _SESSIONS_CACHE:
        return _SESSIONS_CACHE[active_gid]

    if active_gid:
        gdata = database.get_game(active_gid)
        if gdata and gdata.get("state"):
            session = GameSession(gdata["state"])
            _SESSIONS_CACHE[active_gid] = session
            return session

    # If no active game, initialize default 2026 scenario
    return create_new_game(user_id, preset_id="modern_2026", player_nation_id="russia")

def create_new_game(
    user_id: int,
    preset_id: str = "modern_2026",
    player_nation_id: str = "russia",
    difficulty: str = "normal"
) -> GameSession:
    """Creates a brand new game session."""
    preset = get_preset_by_id(preset_id)
    game_id = f"game_{user_id}_{int(time.time())}_{uuid.uuid4().hex[:6]}"

    state_dict = {
        "game_id": game_id,
        "user_id": user_id,
        "title": preset.get("name_ru", "Pax Historia 2026"),
        "preset_id": preset_id,
        "current_year": preset.get("start_year", DEFAULT_YEAR),
        "current_month": preset.get("start_month", DEFAULT_MONTH),
        "current_day": preset.get("start_day", DEFAULT_DAY),
        "player_nation": player_nation_id if player_nation_id in preset.get("nations", {}) else list(preset.get("nations", {}).keys())[0],
        "difficulty": difficulty,
        "turn_count": 0,
        "world_tension": 45.0,
        "oil_barrel_price_usd": 82.5,
        "global_trade_growth": 2.1,
        "nations": preset.get("nations", {}),
        "queued_actions": [],
        "recent_events": preset.get("initial_events", []),
        "timeline_log": preset.get("initial_events", []),
        "advisor_history": [],
        "diplomacy_chats": {},
        "frontlines": []
    }

    session = GameSession(state_dict)
    _SESSIONS_CACHE[game_id] = session

    # Save to SQLite
    database.save_or_update_game(
        game_id=game_id,
        user_id=user_id,
        title=session.title,
        preset_id=preset_id,
        year=session.current_year,
        month=session.current_month,
        day=session.current_day,
        player_nation=session.player_nation_id,
        difficulty=difficulty,
        turn_count=0,
        state=session.to_dict(),
        history=session.timeline_log
    )
    database.update_user_settings(user_id, active_game_id=game_id)
    return session

async def submit_action_and_auto_skip(
    user_id: int,
    action_text_or_id: str,
    max_days: int = 30
) -> Tuple[List[Dict[str, Any]], GameSession, int]:
    """
    Core function fulfilling:
    1. Player writes action / prompt / clicks 500+ action
    2. AI executes action AND automatically skips time forward (up to 1 month maximum or as needed)
    3. Simulates month 1 starting context, then month 2+ unscripted random emergent events
    4. Updates state and saves rewind history
    """
    session = get_or_load_session(user_id)
    raw_state = session.to_dict()

    # Check if input is a structured action ID
    structured_act = get_action_by_id(action_text_or_id)
    action_text = structured_act.get("title_ru", action_text_or_id) if structured_act else action_text_or_id

    # If structured action, apply baseline effects directly
    if structured_act and session.player_nation:
        p_dict = session.player_nation.to_dict()
        eff = structured_act.get("effects", {})
        for k, v in eff.items():
            if k in p_dict and isinstance(p_dict[k], (int, float)):
                p_dict[k] = p_dict[k] + v
            elif k in p_dict and isinstance(p_dict[k], bool):
                p_dict[k] = v
            elif k in p_dict and isinstance(p_dict[k], str):
                p_dict[k] = v
        # Update nation state
        session.nations[session.player_nation_id] = CountryState(p_dict)
        raw_state = session.to_dict()

    # Run AI Simulation & Auto Time Advance
    events, updated_state, days_advanced = await AIEngine.simulate_turn_jump(
        user_id=user_id,
        game_state=raw_state,
        player_action_text=action_text,
        days_requested=max_days
    )

    # Advance Date
    session.current_day += days_advanced
    while session.current_day > 30:
        session.current_day -= 30
        session.current_month += 1
        if session.current_month > 12:
            session.current_month = 1
            session.current_year += 1

    session.turn_count += 1
    session.recent_events = events
    session.timeline_log.extend(events)

    # Re-sync nations from updated state
    for nid, ndata in updated_state.get("nations", {}).items():
        session.nations[nid] = CountryState(ndata)

    # Cache and Persist
    _SESSIONS_CACHE[session.game_id] = session
    database.save_or_update_game(
        game_id=session.game_id,
        user_id=user_id,
        title=session.title,
        preset_id=session.preset_id,
        year=session.current_year,
        month=session.current_month,
        day=session.current_day,
        player_nation=session.player_nation_id,
        difficulty=session.difficulty,
        turn_count=session.turn_count,
        state=session.to_dict(),
        history=session.timeline_log
    )

    return events, session, days_advanced

async def manual_time_jump(user_id: int, step_key: str = "1m") -> Tuple[List[Dict[str, Any]], GameSession, int]:
    """Advances time manually according to chosen step."""
    step_info = TIME_STEPS.get(step_key, TIME_STEPS["1m"])
    days = step_info["days"]
    return await submit_action_and_auto_skip(user_id, action_text_or_id="", max_days=days)

def get_full_country_stats(user_id: int, target_nation_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Returns granular 2026 statistics for inspection."""
    session = get_or_load_session(user_id)
    nid = target_nation_id or session.player_nation_id
    nation = session.nations.get(nid)
    if not nation:
        return None
    return nation.to_dict()

def modify_country_stat(
    user_id: int,
    stat_key: str,
    new_value: Any,
    target_nation_id: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Granular Country Stat Modifier:
    Allows user/admin to modify ANY stat (GDP, treasury, internet status, GPS jamming, nukes, stability, army, taxes, etc.).
    """
    session = get_or_load_session(user_id)
    nid = target_nation_id or session.player_nation_id
    nation = session.nations.get(nid)
    if not nation:
        return False, f"Государство {nid} не найдено."

    ndict = nation.to_dict()
    # Type casting
    try:
        if isinstance(ndict.get(stat_key), float) or isinstance(getattr(nation, stat_key, None), float):
            parsed_val = float(new_value)
        elif isinstance(ndict.get(stat_key), int) or isinstance(getattr(nation, stat_key, None), int):
            parsed_val = int(new_value)
        elif isinstance(ndict.get(stat_key), bool) or isinstance(getattr(nation, stat_key, None), bool):
            parsed_val = bool(new_value)
        else:
            parsed_val = new_value
        
        ndict[stat_key] = parsed_val
        setattr(nation, stat_key, parsed_val)
    except Exception as e:
        return False, f"Ошибка преобразования типа: {e}"

    session.nations[nid] = CountryState(ndict)
    _SESSIONS_CACHE[session.game_id] = session

    database.save_or_update_game(
        game_id=session.game_id,
        user_id=user_id,
        title=session.title,
        preset_id=session.preset_id,
        year=session.current_year,
        month=session.current_month,
        day=session.current_day,
        player_nation=session.player_nation_id,
        difficulty=session.difficulty,
        turn_count=session.turn_count,
        state=session.to_dict(),
        history=session.timeline_log
    )

    return True, f"Параметр '{stat_key}' успешно изменен на '{new_value}'!"

def rewind_turns(user_id: int, steps: int = 1) -> Tuple[bool, str, Optional[GameSession]]:
    """Rewinds game state back by N turns."""
    session = get_or_load_session(user_id)
    snapshots = database.get_rewind_snapshots(session.game_id)
    if len(snapshots) <= steps:
        return False, "Недостаточно сохраненных ходов для отката назад.", None

    target_snap = snapshots[steps]
    st = target_snap.get("state", {})
    if not st:
        return False, "Ошибка снимка состояния.", None

    restored_session = GameSession(st)
    _SESSIONS_CACHE[session.game_id] = restored_session
    database.save_or_update_game(
        game_id=restored_session.game_id,
        user_id=user_id,
        title=restored_session.title,
        preset_id=restored_session.preset_id,
        year=restored_session.current_year,
        month=restored_session.current_month,
        day=restored_session.current_day,
        player_nation=restored_session.player_nation_id,
        difficulty=restored_session.difficulty,
        turn_count=restored_session.turn_count,
        state=restored_session.to_dict(),
        history=restored_session.timeline_log
    )
    return True, f"Успешный откат на {steps} ход(а)! Дата: {restored_session.get_date_str()}", restored_session
