"""
FastAPI Web Server - Live Interactive Web Studio & Telegram Simulator for Pax Historia (2026 Engine)
Runs on 0.0.0.0:8080 for instant live preview and testing.
"""
from fastapi import FastAPI, Request, Response, Body
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import io
import json
from typing import Dict, Any, Optional

import database
from config import WEB_HOST, WEB_PORT, PROMPT_CATEGORIES, SUPPORTED_PROVIDERS, DEFAULT_MODELS, BASE_DIR
from game.presets import get_all_presets, get_preset_by_id
from game.actions_registry import get_all_actions, get_all_categories, get_action_by_id
from game.engine import (
    get_or_load_session, create_new_game, submit_action_and_auto_skip,
    manual_time_jump, modify_country_stat, rewind_turns
)
from game.map_renderer import render_world_map_png, render_world_map_svg
from ai.engine import AIEngine
from ai.prompt_manager import get_default_prompt

app = FastAPI(title="Pax Historia 2026 - Web Studio & Telegram Bot Simulator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(BASE_DIR, "web", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "web", "templates")
INDEX_HTML_PATH = os.path.join(TEMPLATES_DIR, "index.html")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

DEFAULT_DEMO_USER_ID = 10001

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/state")
async def api_get_state(user_id: int = DEFAULT_DEMO_USER_ID):
    session = get_or_load_session(user_id)
    return JSONResponse(session.to_dict())

@app.get("/api/map.png")
async def api_get_map_png(user_id: int = DEFAULT_DEMO_USER_ID):
    session = get_or_load_session(user_id)
    png_bytes = render_world_map_png(session.to_dict())
    return Response(content=png_bytes, media_type="image/png")

@app.get("/api/map.svg")
async def api_get_map_svg(user_id: int = DEFAULT_DEMO_USER_ID):
    session = get_or_load_session(user_id)
    svg_str = render_world_map_svg(session.to_dict())
    return Response(content=svg_str, media_type="image/svg+xml")

@app.post("/api/action")
async def api_submit_action(payload: Dict[str, Any] = Body(...)):
    user_id = payload.get("user_id", DEFAULT_DEMO_USER_ID)
    action_text = payload.get("action", "")
    max_days = int(payload.get("max_days", 30))

    events, session, days = await submit_action_and_auto_skip(user_id, action_text, max_days=max_days)
    return JSONResponse({
        "status": "success",
        "days_advanced": days,
        "current_date": session.get_date_str(),
        "turn_count": session.turn_count,
        "events": events,
        "state": session.to_dict()
    })

@app.post("/api/stat_modify")
async def api_stat_modify(payload: Dict[str, Any] = Body(...)):
    user_id = payload.get("user_id", DEFAULT_DEMO_USER_ID)
    stat_key = payload.get("stat_key", "")
    new_value = payload.get("new_value")
    target_nid = payload.get("nation_id")

    ok, msg = modify_country_stat(user_id, stat_key, new_value, target_nid)
    session = get_or_load_session(user_id)
    return JSONResponse({"success": ok, "message": msg, "state": session.to_dict()})

@app.get("/api/actions_catalog")
async def api_get_actions():
    return JSONResponse({
        "categories": get_all_categories(),
        "actions": get_all_actions(),
        "total_count": len(get_all_actions())
    })

@app.get("/api/prompts")
async def api_get_prompts(user_id: int = DEFAULT_DEMO_USER_ID):
    user_prompts = database.get_user_custom_prompts(user_id)
    result = {}
    for cat in PROMPT_CATEGORIES:
        result[cat] = user_prompts.get(cat, get_default_prompt(cat))
    return JSONResponse({"categories": PROMPT_CATEGORIES, "prompts": result})

@app.post("/api/prompts")
async def api_set_prompt(payload: Dict[str, Any] = Body(...)):
    user_id = payload.get("user_id", DEFAULT_DEMO_USER_ID)
    pcat = payload.get("category", "")
    ptext = payload.get("text", "")
    database.set_user_custom_prompt(user_id, pcat, ptext)
    return JSONResponse({"status": "success", "category": pcat})

@app.post("/api/ai_config")
async def api_set_ai_config(payload: Dict[str, Any] = Body(...)):
    user_id = payload.get("user_id", DEFAULT_DEMO_USER_ID)
    provider = payload.get("provider", "builtin")
    model = payload.get("model", "builtin-pro-neural-2026")
    api_key = payload.get("api_key")
    endpoint = payload.get("endpoint")
    temp = float(payload.get("temperature", 0.7))

    database.update_user_settings(
        user_id=user_id,
        ai_provider=provider,
        ai_model=model,
        ai_api_key=api_key,
        ai_endpoint=endpoint,
        ai_temperature=temp
    )
    return JSONResponse({"status": "success", "provider": provider, "model": model})

@app.post("/api/advisor")
async def api_consult_advisor(payload: Dict[str, Any] = Body(...)):
    user_id = payload.get("user_id", DEFAULT_DEMO_USER_ID)
    query = payload.get("query", "Общая оценка")
    session = get_or_load_session(user_id)
    p = session.player_nation
    resp = await AIEngine.consult_advisor(user_id, p.name_ru, p.leader, p.to_dict(), query)
    return JSONResponse({"response": resp})

@app.post("/api/diplomacy")
async def api_chat_diplomacy(payload: Dict[str, Any] = Body(...)):
    user_id = payload.get("user_id", DEFAULT_DEMO_USER_ID)
    target_nid = payload.get("target_nation_id", "usa")
    message = payload.get("message", "Приветствие")
    session = get_or_load_session(user_id)
    p = session.player_nation
    target = session.nations.get(target_nid)
    resp = await AIEngine.chat_diplomacy(user_id, p.name_ru, target_nid, target.to_dict() if target else {}, message)
    return JSONResponse({"response": resp})

@app.post("/api/rewind")
async def api_rewind(payload: Dict[str, Any] = Body(...)):
    user_id = payload.get("user_id", DEFAULT_DEMO_USER_ID)
    steps = int(payload.get("steps", 1))
    ok, msg, sess = rewind_turns(user_id, steps)
    return JSONResponse({"success": ok, "message": msg, "state": sess.to_dict() if sess else {}})

@app.post("/api/newgame")
async def api_new_game(payload: Dict[str, Any] = Body(...)):
    user_id = payload.get("user_id", DEFAULT_DEMO_USER_ID)
    preset_id = payload.get("preset_id", "modern_2026")
    nation_id = payload.get("nation_id", "russia")
    session = create_new_game(user_id, preset_id, nation_id)
    return JSONResponse({"status": "success", "state": session.to_dict()})

@app.get("/api/presets")
async def api_get_presets():
    return JSONResponse(get_all_presets())
