"""
Telegram Bot Handlers - /start, /help, Main Dashboard & Navigation
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database
from game.engine import get_or_load_session
from game.map_renderer import render_world_map_png

def get_main_menu_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Generates the primary Pax Historia dashboard inline keyboard."""
    buttons = [
        [
            InlineKeyboardButton("⚡ Быстрый ход (Авто-скип)", callback_data="game_quick_jump"),
            InlineKeyboardButton("📝 Приказ / Промпт", callback_data="game_write_action")
        ],
        [
            InlineKeyboardButton("🎖️ Советник ИИ", callback_data="menu_advisor"),
            InlineKeyboardButton("🤝 Дипломатия", callback_data="menu_diplomacy")
        ],
        [
            InlineKeyboardButton("🗺️ Карта мира", callback_data="menu_map"),
            InlineKeyboardButton("📊 Статистика страны", callback_data="menu_country_stats")
        ],
        [
            InlineKeyboardButton("🌐 Глушение & РЭБ", callback_data="menu_internet_jamming"),
            InlineKeyboardButton("⚡ Каталог 500+ Действий", callback_data="menu_actions_catalog_0")
        ],
        [
            InlineKeyboardButton("🤖 Настройки ИИ (BYOK)", callback_data="menu_ai_settings"),
            InlineKeyboardButton("📜 Промпты ИИ", callback_data="menu_prompts_editor")
        ],
        [
            InlineKeyboardButton("🌍 Сценарии / Пресеты", callback_data="menu_presets"),
            InlineKeyboardButton("⏪ Откат хода (Rewind)", callback_data="game_rewind_menu")
        ],
        [
            InlineKeyboardButton("💾 Сохранения", callback_data="menu_saves"),
            InlineKeyboardButton("👑 Чит-меню (God Mode)", callback_data="menu_cheats")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /start command."""
    user = update.effective_user
    database.get_or_create_user(user.id, user.username)
    session = get_or_load_session(user.id)
    p_nation = session.player_nation
    
    welcome_text = (
        f"🏛️ **ДОБРО ПОЖАЛОВАТЬ В PAX HISTORIA 2026!**\n\n"
        f"Вы стоите во главе государства **{p_nation.name_ru if p_nation else 'Россия'}** ({p_nation.flag_emoji if p_nation else '🇷🇺'}).\n"
        f"📅 **Дата:** `{session.get_date_str()}` | **Ход:** `#{session.turn_count}`\n"
        f"👑 **Лидер:** `{p_nation.leader if p_nation else 'Владимир Путин'}`\n\n"
        f"📊 **Краткая сводка:**\n"
        f"• ВВП: `${p_nation.gdp_billions:,.0f}B` (Рост: `+{p_nation.gdp_growth}%`)\n"
        f"• Казна: `${p_nation.treasury_billions:,.0f}B` | Стабильность: `{p_nation.stability:.0f}%`\n"
        f"• Армия: `{p_nation.army_divisions} див.` | Рои Дронов: `{p_nation.drone_swarms}`\n"
        f"• Статус Интернета: `{p_nation.internet_status}` | РЭБ/GPS: `{'АКТИВНО 🛰️' if p_nation.gps_jamming_active else 'ВЫКЛ 🟢'}`\n\n"
        f"💡 **Особенности симулятора:**\n"
        f"1. ⚡ **Авто-скип времени:** При отправке любого текста/промпта ИИ автоматически продвинет время (до 1 месяца) и покажет последствия.\n"
        f"2. 🎲 **Нелинейная песочница:** Месяц 1 начинается по контексту, а затем мир переходит в 100% случайную динамическую симуляцию!\n"
        f"3. 🌐 **Глушение интернета, РЭБ и взломы.**\n"
        f"4. ⚙️ **Просмотр и изменение любой статистики страны.**\n"
        f"5. 🤖 **Подключение своего ИИ (OpenAI, OpenRouter, Groq, Anthropic, DeepSeek, Ollama, Custom URL) и редактор промптов.**\n"
        f"6. 📚 **Более 500 доступных действий.**"
    )

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /help command."""
    help_text = (
        "📖 **РУКОВОДСТВО ПО PAX HISTORIA 2026**\n\n"
        "🎮 **Основные команды:**\n"
        "• `/start` — Главное меню и оперативная сводка\n"
        "• `/map` — Графическая карта мира и линии фронта\n"
        "• `/action <текст>` — Отдать приказ с авто-скипом времени до 1 месяца\n"
        "• `/advisor <вопрос>` — Спросить совет у стратегического ИИ-штаба\n"
        "• `/diplomacy` — Переговоры с мировыми лидерами и саммиты\n"
        "• `/status` — Полная статистика и аналитика государства\n"
        "• `/stats` — Редактор параметров страны (изменить ВВП, армию, казну)\n"
        "• `/jump` — Ручной скачок времени вперед\n"
        "• `/rewind` — Откат на предыдущий ход (исправление ошибок)\n"
        "• `/ai` — Настройка своего ИИ и API-ключей (BYOK)\n"
        "• `/prompts` — Редактор системных промптов симулятора\n"
        "• `/presets` — Выбор сценария (2026, 1936, 1914, Рим, 2666)\n"
        "• `/cheats` — Режим бога и чит-коды"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def cmd_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends fresh visual world map photo."""
    user = update.effective_user
    session = get_or_load_session(user.id)
    img_bytes = render_world_map_png(session.to_dict())
    
    caption = (
        f"🗺️ **ОПЕРАТИВНАЯ КАРТА МИРА 2026**\n"
        f"📅 `{session.get_date_str()}` | **Ход:** `#{session.turn_count}`\n"
        f"⚔️ **Фронты:** Россия-Украина, Ближний Восток\n"
        f"📶 **РЭБ/Глушение:** `{'АКТИВНО 🛰️' if session.player_nation.gps_jamming_active else 'ВЫКЛ 🟢'}`"
    )
    await update.message.reply_photo(photo=img_bytes, caption=caption, parse_mode="Markdown")
