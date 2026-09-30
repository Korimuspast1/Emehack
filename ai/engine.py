"""
Unified AI Engine for Pax Historia (2026 Engine)
Orchestrates Custom LLMs (OpenAI, Anthropic, OpenRouter, Groq, DeepSeek, Ollama, Custom URL)
with Built-in Procedural Alternate History Simulation Fallback.
"""
import json
from typing import Dict, List, Any, Optional, Tuple
from config import AI_PROVIDER_BUILTIN
import database
from ai.prompt_manager import get_default_prompt, interpolate_prompt
from ai.provider_client import call_external_llm
from ai.builtin_sim import (
    simulate_jump_step, generate_advisor_counsel, generate_leader_dialogue,
    brainstorm_strategic_actions, enhance_player_action_text
)

class AIEngine:
    @staticmethod
    async def get_user_ai_config(user_id: int) -> Dict[str, Any]:
        user = database.get_or_create_user(user_id)
        return {
            "provider": user.get("ai_provider", AI_PROVIDER_BUILTIN),
            "model": user.get("ai_model", "builtin-pro-neural-2026"),
            "api_key": user.get("ai_api_key"),
            "endpoint": user.get("ai_endpoint"),
            "temperature": float(user.get("ai_temperature", 0.7))
        }

    @staticmethod
    async def get_prompt(user_id: int, prompt_key: str) -> str:
        custom_prompts = database.get_user_custom_prompts(user_id)
        if prompt_key in custom_prompts and custom_prompts[prompt_key].strip():
            return custom_prompts[prompt_key]
        return get_default_prompt(prompt_key)

    @classmethod
    async def simulate_turn_jump(
        cls,
        user_id: int,
        game_state: Dict[str, Any],
        player_action_text: str,
        days_requested: int = 30
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any], int]:
        """Runs the time progression step and generates narrative world events."""
        ai_cfg = await cls.get_user_ai_config(user_id)
        is_month_one = (game_state.get("turn_count", 0) < 1)

        # First run simulation logic & state updates
        events, updated_state, actual_days = simulate_jump_step(
            game_state, player_action_text, days_requested, is_month_one=is_month_one
        )

        # If external LLM is configured, enrich events with LLM narrative
        if ai_cfg["provider"] != AI_PROVIDER_BUILTIN and ai_cfg.get("api_key"):
            template = await cls.get_prompt(user_id, "jump_forward")
            p_nid = updated_state.get("player_nation", "russia")
            p_nation = updated_state.get("nations", {}).get(p_nid, {})

            context = {
                "DATE": f"{updated_state.get('current_day', 1)}/{updated_state.get('current_month', 1)}/{updated_state.get('current_year', 2026)}",
                "NATION": p_nation.get("name_ru", "Россия"),
                "LEADER": p_nation.get("leader", "Лидер"),
                "IDEOLOGY": p_nation.get("ideology", "Консерватизм"),
                "STABILITY": p_nation.get("stability", 75),
                "GDP": p_nation.get("gdp_billions", 500),
                "TREASURY": p_nation.get("treasury_billions", 50),
                "ARMY_DIVISIONS": p_nation.get("army_divisions", 50),
                "INTERNET_STATUS": p_nation.get("internet_status", "ONLINE"),
                "GPS_JAMMING": "АКТИВНО" if p_nation.get("gps_jamming_active") else "ВЫКЛ",
                "WARS": ", ".join(p_nation.get("at_war", [])) or "Нет",
                "ALLIES": ", ".join(p_nation.get("allies", [])) or "Нет",
                "PLAYER_ACTION": player_action_text or "Стандартное государственное управление"
            }
            prompt_str = interpolate_prompt(template, context)
            llm_resp = await call_external_llm(
                provider=ai_cfg["provider"],
                api_key=ai_cfg["api_key"],
                model=ai_cfg["model"],
                prompt=prompt_str,
                custom_endpoint=ai_cfg["endpoint"],
                temperature=ai_cfg["temperature"]
            )
            if llm_resp and len(llm_resp.strip()) > 50:
                events.insert(0, {
                    "title_ru": "🌐 Сводка глобальной симуляции (ИИ)",
                    "title_en": "🌐 Global Simulation Intelligence Briefing (AI)",
                    "text_ru": llm_resp.strip(),
                    "text_en": llm_resp.strip(),
                    "type": "ai_grand_narrative"
                })

        return events, updated_state, actual_days

    @classmethod
    async def chat_diplomacy(
        cls,
        user_id: int,
        player_nation_name: str,
        target_nation_id: str,
        target_nation_data: Dict[str, Any],
        user_message: str
    ) -> str:
        """Conducts diplomatic chat with foreign leader."""
        ai_cfg = await cls.get_user_ai_config(user_id)
        target_name = target_nation_data.get("name_ru", target_nation_id)
        target_leader = target_nation_data.get("leader", "Лидер")
        relations = target_nation_data.get("relations", {}).get(player_nation_name, 0)

        if ai_cfg["provider"] != AI_PROVIDER_BUILTIN and ai_cfg.get("api_key"):
            template = await cls.get_prompt(user_id, "chat_diplomacy")
            context = {
                "TARGET_NATION": target_name,
                "TARGET_LEADER": target_leader,
                "NATION": player_nation_name,
                "RELATIONS_SCORE": relations,
                "DIPLOMATIC_STATUS": "Война" if relations < -50 else "Союз" if relations > 50 else "Нейтралитет",
                "USER_MESSAGE": user_message
            }
            prompt_str = interpolate_prompt(template, context)
            resp = await call_external_llm(
                provider=ai_cfg["provider"],
                api_key=ai_cfg["api_key"],
                model=ai_cfg["model"],
                prompt=prompt_str,
                custom_endpoint=ai_cfg["endpoint"],
                temperature=ai_cfg["temperature"]
            )
            if resp:
                return resp

        # Fallback to Built-in neural simulator
        return generate_leader_dialogue(
            player_nation=player_nation_name,
            target_nation=target_name,
            target_leader=target_leader,
            relations=relations,
            user_message=user_message
        )

    @classmethod
    async def consult_advisor(
        cls,
        user_id: int,
        nation_name: str,
        leader: str,
        stats: Dict[str, Any],
        query: str
    ) -> str:
        """Consults the AI strategic advisor."""
        ai_cfg = await cls.get_user_ai_config(user_id)
        if ai_cfg["provider"] != AI_PROVIDER_BUILTIN and ai_cfg.get("api_key"):
            template = await cls.get_prompt(user_id, "chat_advisor")
            context = {
                "NATION": nation_name,
                "LEADER": leader,
                "GDP": stats.get("gdp_billions", 500),
                "TREASURY": stats.get("treasury_billions", 50),
                "STABILITY": stats.get("stability", 75),
                "ARMY_DIVISIONS": stats.get("army_divisions", 50),
                "INTERNET_STATUS": stats.get("internet_status", "ONLINE"),
                "WARS": ", ".join(stats.get("at_war", [])) or "Нет",
                "ALLIES": ", ".join(stats.get("allies", [])) or "Нет",
                "USER_QUERY": query
            }
            prompt_str = interpolate_prompt(template, context)
            resp = await call_external_llm(
                provider=ai_cfg["provider"],
                api_key=ai_cfg["api_key"],
                model=ai_cfg["model"],
                prompt=prompt_str,
                custom_endpoint=ai_cfg["endpoint"],
                temperature=ai_cfg["temperature"]
            )
            if resp:
                return resp

        return generate_advisor_counsel(
            nation_name=nation_name,
            leader=leader,
            stats=stats,
            query=query
        )

    @classmethod
    async def brainstorm_actions(cls, user_id: int, nation_name: str, stats: Dict[str, Any]) -> List[str]:
        """Brainstorms 5 strategic actions."""
        return brainstorm_strategic_actions(nation_name, stats)

    @classmethod
    async def enhance_action(cls, user_id: int, draft_text: str, nation_name: str) -> str:
        """Polishes player action text."""
        ai_cfg = await cls.get_user_ai_config(user_id)
        if ai_cfg["provider"] != AI_PROVIDER_BUILTIN and ai_cfg.get("api_key"):
            template = await cls.get_prompt(user_id, "action_enhance")
            context = {
                "NATION": nation_name,
                "DRAFT_ACTION": draft_text
            }
            prompt_str = interpolate_prompt(template, context)
            resp = await call_external_llm(
                provider=ai_cfg["provider"],
                api_key=ai_cfg["api_key"],
                model=ai_cfg["model"],
                prompt=prompt_str,
                custom_endpoint=ai_cfg["endpoint"],
                temperature=ai_cfg["temperature"]
            )
            if resp:
                return resp

        return enhance_player_action_text(draft_text, nation_name)
