"""
Telegram Bot Handlers - Sandbox Cheats & God Mode
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from game.engine import get_or_load_session, modify_country_stat

async def cmd_cheats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /cheats command."""
    user = update.effective_user
    session = get_or_load_session(user.id)
    p = session.player_nation

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💵 +$10,000 Млрд в казну", callback_data="cheat_money"), InlineKeyboardButton("🛡️ 100% Стабильность & 1000 PP", callback_data="cheat_stability_pp")],
        [InlineKeyboardButton("🪖 +100 Дивизий & 500 Роев Дронов", callback_data="cheat_military"), InlineKeyboardButton("☢️ +5,000 Ядерных боеголовок", callback_data="cheat_nukes")],
        [InlineKeyboardButton("🔬 Открыть ВСЕ технологии", callback_data="cheat_tech_all"), InlineKeyboardButton("🕊️ Принудительный Мир во всем мире", callback_data="cheat_force_peace")],
        [InlineKeyboardButton("👑 Мгновенно аннексировать соседа", callback_data="cheat_annex_menu")],
        [InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
    ])

    text = (
        f"👑 **РЕЖИМ БОГА И ЧИТ-МЕНЮ (SANDBOX GOD MODE)**\n\n"
        f"Держава: `{p.name_ru}`\n\n"
        f"Выберите чит-код для мгновенного изменения мирового баланса:"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)

async def handle_cheats_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Dispatches cheats and god mode execution."""
    query = update.callback_query
    data = query.data
    user = update.effective_user
    session = get_or_load_session(user.id)
    p = session.player_nation

    if data == "menu_cheats":
        await query.answer()
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💵 +$10,000B Казна", callback_data="cheat_money"), InlineKeyboardButton("🛡️ 100% Стабильность", callback_data="cheat_stability_pp")],
            [InlineKeyboardButton("🪖 +100 Дивизий", callback_data="cheat_military"), InlineKeyboardButton("☢️ +5,000 Ядерных боеголовок", callback_data="cheat_nukes")],
            [InlineKeyboardButton("🔬 Все технологии", callback_data="cheat_tech_all"), InlineKeyboardButton("🕊️ Мир во всем мире", callback_data="cheat_force_peace")],
            [InlineKeyboardButton("👑 Мгновенная аннексия", callback_data="cheat_annex_menu")],
            [InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
        ])
        await query.edit_message_text(f"👑 **ЧИТ-МЕНЮ (GOD MODE)**\n\nДержава: `{p.name_ru}`", parse_mode="Markdown", reply_markup=kb)
        return True

    elif data == "cheat_money":
        modify_country_stat(user.id, "treasury_billions", p.treasury_billions + 10000.0)
        await query.answer("Чит активирован: +$10,000 Млрд!")
        return await handle_cheats_callbacks(update, context)

    elif data == "cheat_stability_pp":
        modify_country_stat(user.id, "stability", 100.0)
        modify_country_stat(user.id, "political_power", 1000.0)
        await query.answer("Чит активирован: 100% Стабильность и 1000 PP!")
        return await handle_cheats_callbacks(update, context)

    elif data == "cheat_military":
        modify_country_stat(user.id, "army_divisions", p.army_divisions + 100)
        modify_country_stat(user.id, "drone_swarms", p.drone_swarms + 500)
        await query.answer("Чит активирован: +100 дивизий и +500 роев дронов!")
        return await handle_cheats_callbacks(update, context)

    elif data == "cheat_nukes":
        modify_country_stat(user.id, "nuclear_warheads", p.nuclear_warheads + 5000)
        await query.answer("Чит активирован: +5000 боеголовок!")
        return await handle_cheats_callbacks(update, context)

    elif data == "cheat_tech_all":
        modify_country_stat(user.id, "research_points", p.research_points + 5000.0)
        modify_country_stat(user.id, "ai_supremacy_index", 100.0)
        await query.answer("Чит активирован: Все технологии разблокированы!")
        return await handle_cheats_callbacks(update, context)

    elif data == "cheat_force_peace":
        modify_country_stat(user.id, "at_war", [])
        await query.answer("Чит активирован: Все войны завершены!")
        return await handle_cheats_callbacks(update, context)

    elif data == "cheat_annex_menu":
        await query.answer()
        buttons = []
        for nid, nat in session.nations.items():
            if nid != session.player_nation_id:
                buttons.append([InlineKeyboardButton(f"👑 Аннексировать {nat.name_ru}", callback_data=f"cheat_do_annex_{nid}")])
        buttons.append([InlineKeyboardButton("👑 Назад к читам", callback_data="menu_cheats")])
        await query.edit_message_text("👑 **ВЫБЕРИТЕ ГОСУДАРСТВО ДЛЯ МГНОВЕННОЙ АННЕКСИИ:**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))
        return True

    elif data.startswith("cheat_do_annex_"):
        target_nid = data.replace("cheat_do_annex_", "")
        target = session.nations.get(target_nid)
        if target:
            p.gdp_billions += target.gdp_billions
            p.treasury_billions += target.treasury_billions
            p.provinces.extend(target.provinces)
            del session.nations[target_nid]
            await query.answer(f"Государство {target.name_ru} полностью аннексировано!")
        return await handle_cheats_callbacks(update, context)

    return False
