"""
Comprehensive Test Suite for Pax Historia 2026 Engine
"""
import pytest
import os
import asyncio
from game.actions_registry import get_all_actions, get_all_categories, get_action_by_id, get_actions_by_category
from game.presets import get_all_presets, get_preset_by_id
from game.state import GameSession, CountryState
from game.engine import (
    create_new_game, submit_action_and_auto_skip, modify_country_stat,
    rewind_turns, get_full_country_stats, manual_time_jump, get_or_load_session
)
from ai.prompt_manager import interpolate_prompt, get_default_prompt, DEFAULT_PROMPTS
from ai.engine import AIEngine
from ai.builtin_sim import brainstorm_strategic_actions, enhance_player_action_text, generate_leader_dialogue, generate_advisor_counsel
from game.map_renderer import render_world_map_png, render_world_map_svg
import database

def test_actions_registry_and_categories():
    actions = get_all_actions()
    categories = get_all_categories()
    assert len(actions) >= 500
    assert len(categories) == 15
    for cat in categories:
        cat_acts = get_actions_by_category(cat["id"])
        assert len(cat_acts) > 0, f"Category {cat['id']} has no actions"

    # Test random action lookup
    act = get_action_by_id("cyber_full_internet_shutdown")
    assert act is not None
    assert act["category"] == "cyber_internet"

def test_preset_modern_2026_and_historical():
    presets = get_all_presets()
    assert len(presets) >= 6

    preset_2026 = get_preset_by_id("modern_2026")
    assert preset_2026["start_year"] == 2026
    assert "russia" in preset_2026["nations"]
    assert "usa" in preset_2026["nations"]
    assert "china" in preset_2026["nations"]

    ru = preset_2026["nations"]["russia"]
    assert ru["gps_jamming_active"] is True
    assert ru["internet_status"] == "ONLINE"
    assert ru["nuclear_warheads"] >= 5000

@pytest.mark.asyncio
async def test_auto_skip_and_unscripted_sandbox():
    user_id = 88888
    session = create_new_game(user_id, preset_id="modern_2026", player_nation_id="russia")
    assert session.current_year == 2026
    assert session.turn_count == 0

    # Turn 1: Action with auto time advance
    events1, s1, days1 = await submit_action_and_auto_skip(
        user_id,
        "Развернуть комплексы РЭБ для глушения GPS/Starlink и запустить производство роев БПЛА"
    )
    assert days1 > 0 and days1 <= 30
    assert s1.turn_count == 1
    assert len(events1) >= 1

    # Turn 2: Unscripted emergent random sandbox mode (Month > 1)
    events2, s2, days2 = await submit_action_and_auto_skip(
        user_id,
        "Инвестировать $50 млрд в разработку квантовых микрочипов и термоядерной энергии"
    )
    assert s2.turn_count == 2
    assert len(events2) >= 1

@pytest.mark.asyncio
async def test_country_stat_inspector_and_modifier():
    user_id = 77777
    session = create_new_game(user_id, preset_id="modern_2026", player_nation_id="russia")

    # Inspect stats
    stats = get_full_country_stats(user_id)
    assert stats is not None
    assert stats["id"] == "russia"

    # Modify multiple stats
    ok, _ = modify_country_stat(user_id, "gdp_billions", 4200.0)
    assert ok is True
    updated = get_or_load_session(user_id)
    assert updated.player_nation.gdp_billions == 4200.0

    ok, _ = modify_country_stat(user_id, "treasury_billions", 950.0)
    assert ok is True
    assert updated.player_nation.treasury_billions == 950.0

    ok, _ = modify_country_stat(user_id, "nuclear_warheads", 6500)
    assert ok is True
    assert updated.player_nation.nuclear_warheads == 6500

    ok, _ = modify_country_stat(user_id, "internet_status", "FULL_SHUTDOWN")
    assert ok is True
    assert updated.player_nation.internet_status == "FULL_SHUTDOWN"

@pytest.mark.asyncio
async def test_rewind_functionality():
    user_id = 66666
    session = create_new_game(user_id, preset_id="modern_2026", player_nation_id="russia")
    
    # Run 3 turns
    await submit_action_and_auto_skip(user_id, "Turn 1 action")
    await submit_action_and_auto_skip(user_id, "Turn 2 action")
    await submit_action_and_auto_skip(user_id, "Turn 3 action")
    
    curr = get_or_load_session(user_id)
    assert curr.turn_count == 3

    # Rewind 1 turn
    ok, msg, restored = rewind_turns(user_id, steps=1)
    assert ok is True
    assert restored.turn_count == 2

def test_ai_builtin_sim_modules():
    stats = {"stability": 80, "gdp_billions": 2450, "treasury_billions": 680, "army_divisions": 115, "internet_status": "ONLINE", "gps_jamming_active": True}
    
    # Advisor
    adv = generate_advisor_counsel("Россия", "Президент", stats, "Военная стратегия")
    assert "СВОДКА ГЕНЕРАЛЬНОГО ШТАБА" in adv

    # Leader dialogue
    lead_friendly = generate_leader_dialogue("Россия", "Китай", "Си Цзиньпин", 85, "Торговый договор")
    assert "Си Цзиньпин" in lead_friendly

    lead_hostile = generate_leader_dialogue("Россия", "США", "Президент США", -80, "Ультиматум")
    assert "Президент США" in lead_hostile

    # Brainstorm
    ideas = brainstorm_strategic_actions("Россия", stats)
    assert len(ideas) == 5

    # Enhance action
    enh = enhance_player_action_text("Построить заводы микрочипов", "Россия")
    assert "Приказ Верховного Главнокомандования Россия" in enh

def test_prompt_customization_and_database():
    user_id = 55555
    database.set_user_custom_prompt(user_id, "jump_forward", "Кастомный промпт для {NATION} в {YEAR}")
    prompts = database.get_user_custom_prompts(user_id)
    assert "jump_forward" in prompts
    assert "Кастомный промпт" in prompts["jump_forward"]

    database.reset_user_custom_prompt(user_id, "jump_forward")
    prompts_after = database.get_user_custom_prompts(user_id)
    assert "jump_forward" not in prompts_after
