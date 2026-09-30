"""
Telegram Bot Application Setup & Dispatcher for Pax Historia (2026 Engine)
"""
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ContextTypes
)

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_PROXY_URL
import database
from game.engine import (
    get_or_load_session, submit_action_and_auto_skip, modify_country_stat
)
from ai.engine import AIEngine
from bot.handlers_start import cmd_start, cmd_help, cmd_map, get_main_menu_keyboard
from bot.handlers_game import cmd_action, cmd_jump, cmd_rewind, handle_game_callbacks
from bot.handlers_country import cmd_status, cmd_stats_edit, handle_country_callbacks
from bot.handlers_advisor import cmd_advisor, handle_advisor_callbacks
from bot.handlers_diplomacy import cmd_diplomacy, handle_diplomacy_callbacks
from bot.handlers_actions_menu import handle_actions_catalog_callbacks
from bot.handlers_ai_prompts import cmd_ai, cmd_prompts, handle_ai_prompts_callbacks
from bot.handlers_scenarios import cmd_presets, handle_scenarios_callbacks
from bot.handlers_cheats import cmd_cheats, handle_cheats_callbacks

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Universal callback query router."""
    query = update.callback_query
    data = query.data

    if data == "menu_main":
        await query.answer()
        user = update.effective_user
        session = get_or_load_session(user.id)
        p = session.player_nation
        text = (
            f"🏛️ **ГЛАВНЫЙ ШТАБ: {p.name_ru.upper()}** ({p.flag_emoji})\n\n"
            f"📅 **Дата:** `{session.get_date_str()}` | **Ход:** `#{session.turn_count}`\n"
            f"👑 **Лидер:** `{p.leader}` | **Идеология:** `{p.ideology}`\n\n"
            f"📊 **Показатели:**\n"
            f"• ВВП: `${p.gdp_billions:,.1f}B` (Рост: `+{p.gdp_growth}%`) | Казна: `${p.treasury_billions:,.1f}B`\n"
            f"• Стабильность: `{p.stability:.0f}%` | Армия: `{p.army_divisions} див.`\n"
            f"• Статус сети: `{p.internet_status}` | РЭБ/GPS: `{'АКТИВНО 🛰️' if p.gps_jamming_active else 'ВЫКЛ 🟢'}`\n\n"
            f"Выберите действие в меню:"
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())
        return

    if data == "menu_map":
        await query.answer()
        user = update.effective_user
        session = get_or_load_session(user.id)
        from game.map_renderer import render_world_map_png
        img_bytes = render_world_map_png(session.to_dict())
        caption = (
            f"🗺️ **ОПЕРАТИВНАЯ КАРТА МИРА 2026**\n"
            f"📅 `{session.get_date_str()}` | **Ход:** `#{session.turn_count}`\n"
            f"📶 **РЭБ/Глушение:** `{'АКТИВНО 🛰️' if session.player_nation.gps_jamming_active else 'ВЫКЛ 🟢'}`"
        )
        await update.effective_chat.send_photo(photo=img_bytes, caption=caption, parse_mode="Markdown")
        return

    if data == "noop":
        await query.answer()
        return

    # Route through modules
    if await handle_game_callbacks(update, context):
        return
    if await handle_country_callbacks(update, context):
        return
    if await handle_advisor_callbacks(update, context):
        return
    if await handle_diplomacy_callbacks(update, context):
        return
    if await handle_actions_catalog_callbacks(update, context):
        return
    if await handle_ai_prompts_callbacks(update, context):
        return
    if await handle_scenarios_callbacks(update, context):
        return
    if await handle_cheats_callbacks(update, context):
        return

    await query.answer("Действие обработано.")

async def handle_free_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles free-text messages (prompts, stat edit, API key, actions)."""
    user = update.effective_user
    text = update.message.text.strip()
    session = get_or_load_session(user.id)
    p = session.player_nation

    # Check state flags
    if context.user_data.get("awaiting_api_key"):
        context.user_data["awaiting_api_key"] = False
        database.update_user_settings(user.id, ai_api_key=text)
        await update.message.reply_text(f"✅ **API Ключ успешно сохранен!**\nТеперь симулятор использует внешнюю нейросеть.", parse_mode="Markdown")
        return

    if context.user_data.get("awaiting_model_id"):
        context.user_data["awaiting_model_id"] = False
        database.update_user_settings(user.id, ai_model=text)
        await update.message.reply_text(f"✅ **Модель изменена на `{text}`!**", parse_mode="Markdown")
        return

    if context.user_data.get("awaiting_prompt_text"):
        pcat = context.user_data["awaiting_prompt_text"]
        context.user_data["awaiting_prompt_text"] = None
        database.set_user_custom_prompt(user.id, pcat, text)
        await update.message.reply_text(f"✅ **Промпт `{pcat}` успешно обновлен!**", parse_mode="Markdown")
        return

    if context.user_data.get("awaiting_advisor_prompt"):
        context.user_data["awaiting_advisor_prompt"] = False
        msg = await update.message.reply_text("🎖️ **Аналитический совет готовит ответ...**", parse_mode="Markdown")
        resp = await AIEngine.consult_advisor(user.id, p.name_ru, p.leader, p.to_dict(), text)
        await msg.edit_text(resp, parse_mode="Markdown")
        return

    if context.user_data.get("awaiting_diplomacy_message"):
        target_nid = context.user_data["awaiting_diplomacy_message"]
        context.user_data["awaiting_diplomacy_message"] = None
        target = session.nations.get(target_nid)
        msg = await update.message.reply_text(f"📬 **Посол передает ноту руководству {target.name_ru if target else ''}...**", parse_mode="Markdown")
        resp = await AIEngine.chat_diplomacy(user.id, p.name_ru, target_nid, target.to_dict() if target else {}, text)
        await msg.edit_text(f"📬 **ОТВЕТ:**\n\n{resp}", parse_mode="Markdown")
        return

    if context.user_data.get("awaiting_stat_edit"):
        context.user_data["awaiting_stat_edit"] = False
        parts = text.split(maxsplit=1)
        if len(parts) == 2:
            s_key, s_val = parts[0], parts[1]
            ok, res_msg = modify_country_stat(user.id, s_key, s_val)
            await update.message.reply_text(res_msg)
        else:
            await update.message.reply_text("❌ Неверный формат. Нужно: `<ключ> <значение>`")
        return

    # Default: Treat text as General Player Action / Prompt with Auto-Time-Skip!
    msg = await update.message.reply_text("⚡ **ИИ обрабатывает приказ и продвигает время симуляции (авто-скип)...**", parse_mode="Markdown")
    events, updated_session, days = await submit_action_and_auto_skip(user.id, action_text_or_id=text)
    up_p = updated_session.player_nation

    report_text = (
        f"⚡ **ПРИКАЗ ВЫПОЛНЕН! ВРЕМЯ ПРОДВИНУТО НА {days} ДНЕЙ**\n"
        f"📅 **Дата:** `{updated_session.get_date_str()}` | **Ход:** `#{updated_session.turn_count}`\n\n"
        f"📊 **Показатели {up_p.name_ru}:**\n"
        f"• ВВП: `${up_p.gdp_billions:,.1f}B` | Казна: `${up_p.treasury_billions:,.1f}B`\n"
        f"• Стабильность: `{up_p.stability:.0f}%` | Армия: `{up_p.army_divisions} див.`\n"
        f"• РЭБ/Глушение: `{'АКТИВНО 🛰️' if up_p.gps_jamming_active else 'ВЫКЛ 🟢'}`\n\n"
        f"📰 **СВОДКА СОБЫТИЙ:**\n"
    )
    for ev in events:
        report_text += f"\n• **{ev.get('title_ru', '')}**\n{ev.get('text_ru', '')}\n"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗺️ Карта мира", callback_data="menu_map"), InlineKeyboardButton("📝 Следующий приказ", callback_data="game_write_action")],
        [InlineKeyboardButton("🎖️ Советник ИИ", callback_data="menu_advisor"), InlineKeyboardButton("⏪ Откат хода", callback_data="game_rewind_1")],
        [InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
    ])
    await msg.edit_text(report_text, parse_mode="Markdown", reply_markup=kb)

def build_bot_application() -> Application:
    """Builds and registers all handlers on the Telegram Bot Application."""
    builder = Application.builder().token(TELEGRAM_BOT_TOKEN)
    if TELEGRAM_PROXY_URL:
        builder = builder.proxy_url(TELEGRAM_PROXY_URL).get_updates_proxy_url(TELEGRAM_PROXY_URL)
        
    app = builder.build()

    # Commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("map", cmd_map))
    app.add_handler(CommandHandler("action", cmd_action))
    app.add_handler(CommandHandler("jump", cmd_jump))
    app.add_handler(CommandHandler("rewind", cmd_rewind))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("stats", cmd_stats_edit))
    app.add_handler(CommandHandler("advisor", cmd_advisor))
    app.add_handler(CommandHandler("diplomacy", cmd_diplomacy))
    app.add_handler(CommandHandler("ai", cmd_ai))
    app.add_handler(CommandHandler("prompts", cmd_prompts))
    app.add_handler(CommandHandler("presets", cmd_presets))
    app.add_handler(CommandHandler("cheats", cmd_cheats))

    # Callbacks
    app.add_handler(CallbackQueryHandler(handle_callback_router))

    # Free text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_free_text_message))

    return app
