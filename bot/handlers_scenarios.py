"""
Telegram Bot Handlers - Scenarios, Presets & World Modding
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from game.presets import get_all_presets, get_preset_by_id
from game.engine import create_new_game, get_or_load_session

async def cmd_presets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /presets command."""
    presets = get_all_presets()
    buttons = []
    for pr in presets:
        buttons.append([InlineKeyboardButton(f"🌍 {pr['name_ru']}", callback_data=f"preset_view_{pr['id']}")])
    buttons.append([InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")])

    text = (
        "🌍 **БИБЛИОТЕКА СЦЕНАРИЕВ PAX HISTORIA**\n\n"
        "Выберите историческую эпоху или альтернативную реальность для начала новой игры:"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

async def handle_scenarios_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Dispatches presets selection and new game creation."""
    query = update.callback_query
    data = query.data
    user = update.effective_user

    if data == "menu_presets":
        await query.answer()
        presets = get_all_presets()
        buttons = []
        for pr in presets:
            buttons.append([InlineKeyboardButton(f"🌍 {pr['name_ru']}", callback_data=f"preset_view_{pr['id']}")])
        buttons.append([InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")])
        await query.edit_message_text(
            "🌍 **БИБЛИОТЕКА СЦЕНАРИЕВ:**\n\nВыберите сценарий для старта:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return True

    elif data.startswith("preset_view_"):
        pid = data.replace("preset_view_", "")
        preset = get_preset_by_id(pid)
        await query.answer()

        buttons = []
        row = []
        for nid, nation in preset.get("nations", {}).items():
            row.append(InlineKeyboardButton(f"{nation.get('flag_emoji', '🏳️')} {nation.get('name_ru', nid)}", callback_data=f"start_game_{pid}_{nid}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)

        buttons.append([InlineKeyboardButton("🌍 Назад к сценариям", callback_data="menu_presets")])

        text = (
            f"🌍 **СЦЕНАРИЙ: {preset['name_ru'].upper()}**\n\n"
            f"📅 **Эра:** `{preset.get('era', '2026')}`\n"
            f"📖 **Описание:** {preset['description_ru']}\n\n"
            f"Выберите державу, которую вы хотите возглавить:"
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))
        return True

    elif data.startswith("start_game_"):
        parts = data.replace("start_game_", "").split("_", 1)
        pid = parts[0]
        # In case preset ID has underscores, find matching nation ID
        preset = get_preset_by_id(pid)
        nid = parts[1] if len(parts) > 1 else list(preset.get("nations", {}).keys())[0]

        session = create_new_game(user_id=user.id, preset_id=pid, player_nation_id=nid)
        p = session.player_nation
        await query.answer("Новая игра запущена!")

        text = (
            f"🚀 **НОВАЯ КАМПАНИЯ НАЧАТА!**\n\n"
            f"🌍 **Сценарий:** `{session.title}`\n"
            f"👑 **Ваша держава:** `{p.name_ru}` ({p.flag_emoji})\n"
            f"📅 **Дата старта:** `{session.get_date_str()}`\n\n"
            f"Вам доступны все 500+ действий, глушение интернета, ИИ-советник и свободные приказы!"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗺️ Карта", callback_data="menu_map"), InlineKeyboardButton("📝 Первый приказ", callback_data="game_write_action")],
            [InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        return True

    return False
