"""
Telegram Bot Handlers - 500+ Categorized Actions Browser & Executor
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from game.actions_registry import get_all_categories, get_actions_by_category, get_action_by_id
from game.engine import submit_action_and_auto_skip, get_or_load_session

PAGE_SIZE = 6

async def handle_actions_catalog_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Handles browsing and executing from the 500+ structured actions database."""
    query = update.callback_query
    data = query.data
    user = update.effective_user

    if data.startswith("menu_actions_catalog_"):
        cat_idx = int(data.replace("menu_actions_catalog_", ""))
        categories = get_all_categories()
        
        if cat_idx >= len(categories):
            cat_idx = 0

        current_cat = categories[cat_idx]
        cat_id = current_cat["id"]
        actions = get_actions_by_category(cat_id)

        # Build Category Buttons Grid
        kb = []
        # Category Selector Row
        prev_cat = (cat_idx - 1) % len(categories)
        next_cat = (cat_idx + 1) % len(categories)
        kb.append([
            InlineKeyboardButton("◀️ Категория", callback_data=f"menu_actions_catalog_{prev_cat}"),
            InlineKeyboardButton(f"📂 {cat_idx+1}/{len(categories)}", callback_data="noop"),
            InlineKeyboardButton("Категория ▶️", callback_data=f"menu_actions_catalog_{next_cat}")
        ])

        # Action items buttons (first 6)
        for act in actions[:PAGE_SIZE]:
            kb.append([InlineKeyboardButton(f"⚡ {act['title_ru'][:40]}", callback_data=f"exec_act_{act['id']}")])

        kb.append([
            InlineKeyboardButton("✍️ Свой свободный приказ", callback_data="game_write_action"),
            InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")
        ])

        text = (
            f"⚡ **КАТАЛОГ 500+ ГОСУДАРСТВЕННЫХ ДЕЙСТВИЙ (PAX HISTORIA)**\n\n"
            f"📁 **Текущий раздел:** `{current_cat['name_ru']}`\n"
            f"📊 Всего действий в разделе: `{len(actions)}`\n\n"
            f"Нажмите на любое действие для мгновенного исполнения и авто-скипа хода (до 1 месяца):"
        )

        await query.answer()
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
        return True

    elif data.startswith("exec_act_"):
        act_id = data.replace("exec_act_", "")
        act = get_action_by_id(act_id)
        if not act:
            await query.answer("Действие не найдено.")
            return True

        await query.answer("Исполняем директиву и продвигаем время...")
        events, session, days = await submit_action_and_auto_skip(user.id, action_text_or_id=act_id)
        p = session.player_nation

        text = (
            f"⚡ **ДИРЕКТИВА ВЫПОЛНЕНА: {act['title_ru']}**\n"
            f"⏳ Время продвинуто на `{days} дней` | Дата: `{session.get_date_str()}`\n\n"
            f"📊 **Показатели {p.name_ru}:**\n"
            f"• ВВП: `${p.gdp_billions:,.1f}B` | Казна: `${p.treasury_billions:,.1f}B`\n"
            f"• Стабильность: `{p.stability:.0f}%` | Армия: `{p.army_divisions} див.`\n"
            f"• РЭБ/Глушение: `{'АКТИВНО 🛰️' if p.gps_jamming_active else 'ВЫКЛ 🟢'}`\n\n"
            f"📰 **СВОДКА СОБЫТИЙ:**\n"
        )
        for ev in events:
            text += f"\n• **{ev.get('title_ru', '')}**\n{ev.get('text_ru', '')}\n"

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗺️ Карта", callback_data="menu_map"), InlineKeyboardButton("⚡ Еще действие", callback_data="menu_actions_catalog_0")],
            [InlineKeyboardButton("⏪ Откат (Rewind)", callback_data="game_rewind_1"), InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        return True

    return False
