"""
Pax Historia Telegram Bot - Configuration & Constants (2026 Edition)
"""
import os
from typing import Dict, Any

# Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv(
    "BOT_TOKEN", 
    "7389083158:AAEz8Dqw0WPn6RBu4rzGDXWtBaU_pVEKLmM"
)

DATABASE_PATH = os.getenv("DATABASE_PATH", "/home/user/Emehack/data/pax_historia.db")
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", "8080"))

# Default Start Year & Scenario
DEFAULT_SCENARIO_ID = "modern_2026"
DEFAULT_YEAR = 2026
DEFAULT_MONTH = 1
DEFAULT_DAY = 1

# AI Providers Constants
AI_PROVIDER_BUILTIN = "builtin"
AI_PROVIDER_OPENROUTER = "openrouter"
AI_PROVIDER_OPENAI = "openai"
AI_PROVIDER_ANTHROPIC = "anthropic"
AI_PROVIDER_GROQ = "groq"
AI_PROVIDER_DEEPSEEK = "deepseek"
AI_PROVIDER_OLLAMA = "ollama"
AI_PROVIDER_CUSTOM = "custom"

SUPPORTED_PROVIDERS = [
    AI_PROVIDER_BUILTIN,
    AI_PROVIDER_OPENROUTER,
    AI_PROVIDER_OPENAI,
    AI_PROVIDER_ANTHROPIC,
    AI_PROVIDER_GROQ,
    AI_PROVIDER_DEEPSEEK,
    AI_PROVIDER_OLLAMA,
    AI_PROVIDER_CUSTOM
]

DEFAULT_MODELS: Dict[str, str] = {
    AI_PROVIDER_BUILTIN: "builtin-pro-neural-2026",
    AI_PROVIDER_OPENROUTER: "google/gemini-2.0-flash-001",
    AI_PROVIDER_OPENAI: "gpt-4o-mini",
    AI_PROVIDER_ANTHROPIC: "claude-3-5-haiku-20241022",
    AI_PROVIDER_GROQ: "llama-3.3-70b-versatile",
    AI_PROVIDER_DEEPSEEK: "deepseek-chat",
    AI_PROVIDER_OLLAMA: "llama3",
    AI_PROVIDER_CUSTOM: "default-model"
}

# 12 Pax Historia Prompt Categories
PROMPT_CATEGORIES = [
    "jump_forward",           # Time progression & geopolitical butterfly effect
    "chat_diplomacy",         # 1-on-1 diplomatic negotiations with foreign leaders
    "chat_advisor",           # Strategic counselor & intelligence briefings
    "action_enhance",         # AI optimizes and adds doctrine nuance to player actions
    "action_brainstorm",      # AI generates 5 tailored strategic recommendations
    "description_to_action",  # Parses free-text directives into stat changes
    "summit_speaker",         # Multi-nation UN/Summit conference dialogues
    "event_consolidator",     # Context compression & memory bank
    "war_resolution",         # Tactical combat & frontline calculation
    "peace_treaty",           # Post-war negotiation terms
    "espionage_operation",    # Cyber attacks, internet jamming, covert ops
    "custom_event"            # Sandbox world crisis triggers
]

# Difficulties
DIFFICULTY_VERY_EASY = "very_easy"
DIFFICULTY_EASY = "easy"
DIFFICULTY_NORMAL = "normal"
DIFFICULTY_HARD = "hard"
DIFFICULTY_IMPOSSIBLE = "impossible"

DIFFICULTIES = [
    DIFFICULTY_VERY_EASY,
    DIFFICULTY_EASY,
    DIFFICULTY_NORMAL,
    DIFFICULTY_HARD,
    DIFFICULTY_IMPOSSIBLE
]

# Time Jump Steps
TIME_STEPS = {
    "1w": {"days": 7, "label_ru": "⚡ 1 Неделя", "label_en": "⚡ 1 Week"},
    "1m": {"days": 30, "label_ru": "📅 1 Месяц", "label_en": "📅 1 Month"},
    "3m": {"days": 90, "label_ru": "🍂 3 Месяца", "label_en": "🍂 3 Months"},
    "6m": {"days": 180, "label_ru": "❄️ 6 Месяцев", "label_en": "❄️ 6 Months"},
    "1y": {"days": 365, "label_ru": "⏳ 1 Год", "label_en": "⏳ 1 Year"},
    "5y": {"days": 1825, "label_ru": "🏛️ 5 Лет", "label_en": "🏛️ 5 Years"},
    "event": {"days": 45, "label_ru": "🎯 До ключевого события", "label_en": "🎯 To Major Event"}
}
