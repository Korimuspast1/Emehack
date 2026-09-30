"""
Telegram Bot Handlers - Diplomacy, Bilateral Leader Talks & World Summits
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from game.engine import get_or_load_session
from ai.engine import AIEngine

async def cmd_diplomacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /diplomacy command."""
    user = update.effective_user
    session = get_or_load_session(user.id)
    p = session.player_nation

    buttons = []
    row = []
    for nid, nation in session.nations.items():
        if nid != session.player_nation_id:
            row.append(InlineKeyboardButton(f"{nation.flag_emoji} {nation.name_ru}", callback_data=f"dip_select_{nid}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton("🌐 Международный Саммит ООН / БРИКС", callback_data="dip_summit_open")])
    buttons.append([InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")])

    await update.message.reply_text(
        f"🤝 **ДИПЛОМАТИЧЕСКИЙ КОРПУС ДЕРЖАВЫ {p.name_ru.upper()}**\n\n"
        f"Выберите иностранное государство для двусторонних переговоров с лидером, "
        f"заключения договоров или выдвижения ультиматумов:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_diplomacy_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Dispatches diplomacy and leader chat callback queries."""
    query = update.callback_query
    data = query.data
    user = update.effective_user
    session = get_or_load_session(user.id)
    p = session.player_nation

    if data == "menu_diplomacy":
        await query.answer()
        buttons = []
        row = []
        for nid, nation in session.nations.items():
            if nid != session.player_nation_id:
                row.append(InlineKeyboardButton(f"{nation.flag_emoji} {nation.name_ru}", callback_data=f"dip_select_{nid}"))
                if len(row) == 2:
                    buttons.append(row)
                    row = []
        if row:
            buttons.append(row)
        buttons.append([InlineKeyboardButton("🌐 Международный Саммит ООН", callback_data="dip_summit_open")])
        buttons.append([InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")])

        await query.edit_message_text(
            f"🤝 **ДИПЛОМАТИЧЕСКИЙ ХАБ ({p.name_ru})**\n\n"
            f"Выберите державу для переговоров:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return True

    elif data.startswith("dip_select_"):
        target_nid = data.replace("dip_select_", "")
        target = session.nations.get(target_nid)
        if not target:
            await query.answer("Держава не найдена.")
            return True

        await query.answer()
        context.user_data["active_diplomacy_target"] = target_nid
        rel = target.relations.get(session.player_nation_id, 0)
        status_str = "Война ⚔️" if target_nid in p.at_war else "Союз 🤝" if target_nid in p.allies else "Нейтралитет 🌐"

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Написать послу / лидеру", callback_data=f"dip_chat_prompt_{target_nid}")],
            [InlineKeyboardButton("🤝 Предложить Пакт о ненападении", callback_data=f"dip_quick_pact_{target_nid}")],
            [InlineKeyboardButton("🛡️ Предложить Военный союз", callback_data=f"dip_quick_alliance_{target_nid}")],
            [InlineKeyboardButton("🚫 Ввести тотальное торговое эмбарго", callback_data=f"dip_quick_embargo_{target_nid}")],
            [InlineKeyboardButton("🕊️ Начать мирные переговоры", callback_data=f"dip_quick_peace_{target_nid}")],
            [InlineKeyboardButton("🤝 Назад к списку стран", callback_data="menu_diplomacy")]
        ])

        text = (
            f"🏛️ **ДИПЛОМАТИЧЕСКИЙ КАБИНЕТ: {target.name_ru.upper()}** ({target.flag_emoji})\n\n"
            f"👑 **Глава государства:** `{target.leader}`\n"
            f"📜 **Идеология:** `{target.ideology}`\n"
            f"📊 **Отношения к вам:** `{rel}/100` | **Статус:** `{status_str}`\n"
            f"💰 **ВВП:** `${target.gdp_billions:,.0f}B` | **Армия:** `{target.army_divisions} див.`\n"
            f"📶 **РЭБ/Глушение:** `{'ВКЛЮЧЕНО 🛰️' if target.gps_jamming_active else 'ВЫКЛЮЧЕНО 🟢'}`\n\n"
            f"Выберите дипломатическую инициативу:"
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        return True

    elif data.startswith("dip_chat_prompt_"):
        target_nid = data.replace("dip_chat_prompt_", "")
        target = session.nations.get(target_nid)
        await query.answer()
        context.user_data["awaiting_diplomacy_message"] = target_nid
        await query.edit_message_text(
            f"✍️ **ПРЯМАЯ ДИПЛОМАТИЧЕСКАЯ НОТА К {target.name_ru.upper()} ({target.leader}):**\n\n"
            f"Напишите текст вашего дипломатического обращения, предложения, предупреждения или ультиматума в ответном сообщении.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏛️ Отмена", callback_data=f"dip_select_{target_nid}")]])
        )
        return True

    elif data.startswith("dip_quick_"):
        action_type = data.replace("dip_quick_", "")
        # Parse action and target
        parts = action_type.split("_", 1)
        act = parts[0]
        tnid = parts[1] if len(parts) > 1 else ""
        target = session.nations.get(tnid)

        await query.answer("Отправка дипломатической ноты...")
        msg_str = f"Официальная нота с предложением: {act}"
        resp = await AIEngine.chat_diplomacy(user.id, p.name_ru, tnid, target.to_dict() if target else {}, msg_str)

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Продолжить диалог", callback_data=f"dip_chat_prompt_{tnid}")],
            [InlineKeyboardButton("🤝 Назад к странам", callback_data="menu_diplomacy"), InlineKeyboardButton("🏛️ Меню", callback_data="menu_main")]
        ])
        await query.edit_message_text(f"📬 **ОТВЕТ ИНОСТРАННОГО ЛИДЕРА:**\n\n{resp}", parse_mode="Markdown", reply_markup=kb)
        return True

    elif data == "dip_summit_open":
        await query.answer("Созыв Саммита...")
        text = (
            f"🌐 **ГЛОБАЛЬНЫЙ МЕЖДУНАРОДНЫЙ САММИТ 2026**\n\n"
            f"В зале присутствуют делегации великих держав:\n"
            f"• 🇷🇺 Российская Федерация (Председатель)\n"
            f"• 🇨🇳 Китайская Народная Республика\n"
            f"• 🇺🇸 Соединенные Штаты Америки\n"
            f"• 🇪🇺 Европейский Союз\n"
            f"• 🇮🇳 Республика Индия\n\n"
            f"Повестка дня: Регулирование военного ИИ, безопасность морских путей и снятие взаимных санкций.\n\n"
            f"Нажмите кнопку ниже, чтобы внести проект резолюции:"
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📜 Внести резолюцию {p.name_ru}", callback_data="game_write_action")],
            [InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        return True

    return False
