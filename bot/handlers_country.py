"""
Telegram Bot Handlers - Country Statistics Inspector, Granular Modifier & Cyber/Jamming Controls
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database
from game.engine import get_or_load_session, modify_country_stat

def get_country_stats_formatted(p_nation, lang: str = "ru") -> str:
    """Formats full granular 2026 nation statistics for viewing."""
    res = p_nation.resources
    jamming_str = "🔴 ВКЛЮЧЕНО (Блокировка GPS/Старлинк)" if p_nation.gps_jamming_active else "🟢 ВЫКЛЮЧЕНО (Сигналы открыты)"
    dpi_str = "ВКЛЮЧЕН (Суверенный файрвол)" if p_nation.deep_packet_inspection else "ВЫКЛЮЧЕН"
    martial_str = "🚨 ВВЕДЕНО" if p_nation.martial_law else "🟢 ОТСУТСТВУЕТ"

    text = (
        f"🏛️ **ПОЛНАЯ СТАТИСТИКА ГОСУДАРСТВА: {p_nation.name_ru.upper()}** ({p_nation.flag_emoji})\n"
        f"👑 **Глава государства:** `{p_nation.leader}`\n"
        f"📜 **Идеология / Режим:** `{p_nation.ideology}` ({p_nation.regime_type})\n"
        f"🏛️ **Правящая партия:** `{p_nation.ruling_party}` (Рейтинг: `{p_nation.approval_rating:.1f}%`)\n"
        f"⚖️ **Коррупция:** `{p_nation.corruption_index:.1f}%` | Военное положение: `{martial_str}`\n\n"
        
        f"🌐 **КИБЕРСФЕРА, ИНТЕРНЕТ И РЭБ 2026:**\n"
        f"• Статус сети: `{p_nation.internet_status}` (Свобода интернета: `{p_nation.internet_freedom:.0f}%`)\n"
        f"• Глушение GPS/Спутников: `{jamming_str}`\n"
        f"• DPI / Файрвол: `{dpi_str}`\n"
        f"• Киберзащита: `{p_nation.cyber_defense_level}/10` | Кибератака: `{p_nation.cyber_offense_level}/10`\n"
        f"• Индекс превосходства ИИ: `{p_nation.ai_supremacy_index:.1f}/100`\n\n"
        
        f"💰 **ЭКОНОМИКА И ФИНАНСЫ:**\n"
        f"• Номинальный ВВП: `${p_nation.gdp_billions:,.1f} млрд` (Рост: `+{p_nation.gdp_growth}%`)\n"
        f"• Казна и резервы: `${p_nation.treasury_billions:,.1f} млрд`\n"
        f"• Госдолг к ВВП: `{p_nation.debt_percent_gdp:.1f}%` | Инфляция: `{p_nation.inflation_percent:.1f}%`\n"
        f"• Налог на прибыль: `{p_nation.tax_rate_corporate:.1f}%` | Подоходный: `{p_nation.tax_rate_income:.1f}%`\n"
        f"• Золотой запас: `{p_nation.gold_reserves_tons:,.0f} тонн`\n\n"

        f"👥 **ОБЩЕСТВО И ДЕМОГРАФИЯ:**\n"
        f"• Население: `{p_nation.population_millions:.1f} млн` | Резерв: `{p_nation.manpower_thousands:,.0f} тыс.`\n"
        f"• Стабильность: `{p_nation.stability:.1f}%` | Поддержка войны: `{p_nation.war_support:.1f}%`\n"
        f"• Политическая власть (PP): `{p_nation.political_power:.0f}/1000`\n"
        f"• Качество жизни: `{p_nation.quality_of_life:.1f}/100` | Безработица: `{p_nation.unemployment_rate:.1f}%`\n\n"

        f"⚔️ **ВООРУЖЕННЫЕ СИЛЫ И АРСЕНАЛ:**\n"
        f"• Армейские дивизии: `{p_nation.army_divisions}` | Танковые бригады: `{p_nation.armored_brigades}`\n"
        f"• Рои ударных FPV-дронов: `{p_nation.drone_swarms}`\n"
        f"• ВМФ (Корабли): `{p_nation.navy_ships}` (Авианосцы: `{p_nation.aircraft_carriers}`, Подлодки: `{p_nation.submarines}`)\n"
        f"• Авиаполки: `{p_nation.air_wings}` (Стелс 5/6 пок.: `{p_nation.stealth_jets}`)\n"
        f"• Гиперзвуковые ракеты: `{p_nation.hypersonic_missiles}` | Батареи ПВО/ПРО: `{p_nation.air_defense_batteries}`\n"
        f"• Ядерный арсенал: `{p_nation.nuclear_warheads} боеголовок`\n"
        f"• Военная доктрина: `{p_nation.military_doctrine}`\n\n"

        f"⚡ **СТРАТЕГИЧЕСКИЕ РЕСУРСЫ:**\n"
        f"• Нефть: `{res.get('oil_mbd', 0)} млн барр/день` | Газ: `{res.get('natural_gas_bcm', 0)} млрд м³`\n"
        f"• Редкоземельные металлы: `{res.get('rare_earths_ktons', 0)} тыс. тонн`\n"
        f"• Уран: `{res.get('uranium_tons', 0)} т` | Сталь: `{res.get('steel_mtons', 0)} млн т`\n"
        f"• Микрочипы (Индекс): `{res.get('semiconductors_index', 0)}/100` | Энергосистема: `{res.get('energy_grid_gw', 0)} ГВт`"
    )
    return text

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /status command."""
    user = update.effective_user
    session = get_or_load_session(user.id)
    p_nation = session.player_nation

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚙️ Изменить параметры (Редактор)", callback_data="menu_stat_editor")],
        [InlineKeyboardButton("🌐 Управление глушением интернета", callback_data="menu_internet_jamming")],
        [InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
    ])
    await update.message.reply_text(get_country_stats_formatted(p_nation), parse_mode="Markdown", reply_markup=kb)

async def cmd_stats_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /stats command."""
    await cmd_status(update, context)

async def handle_country_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Dispatches country inspection, stat editing, and cyber/jamming queries."""
    query = update.callback_query
    data = query.data
    user = update.effective_user
    session = get_or_load_session(user.id)
    p = session.player_nation

    if data == "menu_country_stats":
        await query.answer()
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️ Изменить показатели", callback_data="menu_stat_editor")],
            [InlineKeyboardButton("🌐 Глушение & РЭБ", callback_data="menu_internet_jamming")],
            [InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
        ])
        await query.edit_message_text(get_country_stats_formatted(p), parse_mode="Markdown", reply_markup=kb)
        return True

    elif data == "menu_internet_jamming":
        await query.answer()
        jamming_btn = "🟢 Выключить глушение GPS" if p.gps_jamming_active else "🔴 Включить глушение GPS/РЭБ"
        dpi_btn = "🟢 Отключить DPI/Файрвол" if p.deep_packet_inspection else "🔴 Включить DPI/Файрвол"
        net_btn = "🔴 Отключить Интернет (Блэкаут)" if p.internet_status == "ONLINE" else "🟢 Включить Интернет (Online)"

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(jamming_btn, callback_data="toggle_gps_jamming")],
            [InlineKeyboardButton(dpi_btn, callback_data="toggle_dpi_firewall")],
            [InlineKeyboardButton(net_btn, callback_data="toggle_internet_status")],
            [InlineKeyboardButton("⚡ Запустить ИИ-ботнет когнитивной войны", callback_data="action_cyber_ai_disinfo_botnet")],
            [InlineKeyboardButton("💥 Высотный ЭМИ-удар (EMP)", callback_data="action_cyber_emp_atmospheric_burst")],
            [InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
        ])

        text = (
            f"🌐 **КОМАНДНЫЙ ЦЕНТР КИБЕРВОЙНЫ И РЭБ (2026)**\n\n"
            f"📡 **Текущее состояние информационного пространства:**\n"
            f"• Статус интернета: `{p.internet_status}`\n"
            f"• Глушение GPS/ГЛОНАСС/Starlink: `{'ВКЛЮЧЕНО 🔴' if p.gps_jamming_active else 'ВЫКЛЮЧЕНО 🟢'}`\n"
            f"• Глубокая фильтрация DPI: `{'ВКЛЮЧЕНА 🛡️' if p.deep_packet_inspection else 'ОТКЛЮЧЕНА 🟢'}`\n"
            f"• Уровень киберзащиты: `{p.cyber_defense_level}/10`\n"
            f"• Уровень кибератаки: `{p.cyber_offense_level}/10`\n"
            f"• Индекс ИИ-превосходства: `{p.ai_supremacy_index:.1f}/100`\n\n"
            f"Выберите оперативное действие для мгновенного переключения:"
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        return True

    elif data == "toggle_gps_jamming":
        new_val = not p.gps_jamming_active
        modify_country_stat(user.id, "gps_jamming_active", new_val)
        await query.answer(f"Глушение GPS/РЭБ: {'ВКЛЮЧЕНО' if new_val else 'ВЫКЛЮЧЕНО'}!")
        return await handle_country_callbacks(update, context)

    elif data == "toggle_dpi_firewall":
        new_val = not p.deep_packet_inspection
        modify_country_stat(user.id, "deep_packet_inspection", new_val)
        await query.answer(f"DPI Файрвол: {'ВКЛЮЧЕН' if new_val else 'ВЫКЛЮЧЕН'}!")
        return await handle_country_callbacks(update, context)

    elif data == "toggle_internet_status":
        new_val = "FULL_SHUTDOWN" if p.internet_status == "ONLINE" else "ONLINE"
        modify_country_stat(user.id, "internet_status", new_val)
        await query.answer(f"Статус интернета: {new_val}!")
        return await handle_country_callbacks(update, context)

    elif data == "menu_stat_editor":
        await query.answer()
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💵 ВВП: +$500 млрд", callback_data="edit_gdp_plus"), InlineKeyboardButton("💵 Казна: +$100 млрд", callback_data="edit_treasury_plus")],
            [InlineKeyboardButton("🪖 Армия: +25 дивизий", callback_data="edit_army_plus"), InlineKeyboardButton("🦅 Дроны: +50 роев", callback_data="edit_drones_plus")],
            [InlineKeyboardButton("☢️ Ядерные боеголовки: +100", callback_data="edit_nukes_plus"), InlineKeyboardButton("🛡️ Стабильность: 100%", callback_data="edit_stability_max")],
            [InlineKeyboardButton("⚡ Политсила: 1000 PP", callback_data="edit_pp_max"), InlineKeyboardButton("🔬 Научные очки: +500", callback_data="edit_tech_plus")],
            [InlineKeyboardButton("✍️ Ручной ввод любого параметра", callback_data="edit_custom_stat_prompt")],
            [InlineKeyboardButton("🏛️ Назад к статистике", callback_data="menu_country_stats")]
        ])
        await query.edit_message_text(
            "⚙️ **РЕДАКТОР СТАТИСТИКИ СТРАНЫ (GOD-MODE & INSPECTOR)**\n\n"
            "Здесь вы можете изменить абсолютно любой показатель государства в реальном времени:",
            parse_mode="Markdown",
            reply_markup=kb
        )
        return True

    elif data == "edit_gdp_plus":
        modify_country_stat(user.id, "gdp_billions", p.gdp_billions + 500.0)
        await query.answer("ВВП увеличен на +$500B!")
        return await handle_country_callbacks(update, context)

    elif data == "edit_treasury_plus":
        modify_country_stat(user.id, "treasury_billions", p.treasury_billions + 100.0)
        await query.answer("Казна пополнена на +$100B!")
        return await handle_country_callbacks(update, context)

    elif data == "edit_army_plus":
        modify_country_stat(user.id, "army_divisions", p.army_divisions + 25)
        await query.answer("Армия усилена на +25 дивизий!")
        return await handle_country_callbacks(update, context)

    elif data == "edit_drones_plus":
        modify_country_stat(user.id, "drone_swarms", p.drone_swarms + 50)
        await query.answer("Сформировано +50 роев ударных дронов!")
        return await handle_country_callbacks(update, context)

    elif data == "edit_nukes_plus":
        modify_country_stat(user.id, "nuclear_warheads", p.nuclear_warheads + 100)
        await query.answer("Арсенал увеличен на +100 боеголовок!")
        return await handle_country_callbacks(update, context)

    elif data == "edit_stability_max":
        modify_country_stat(user.id, "stability", 100.0)
        await query.answer("Стабильность установлена на 100%!")
        return await handle_country_callbacks(update, context)

    elif data == "edit_pp_max":
        modify_country_stat(user.id, "political_power", 1000.0)
        await query.answer("Политсила установлена на 1000 PP!")
        return await handle_country_callbacks(update, context)

    elif data == "edit_tech_plus":
        modify_country_stat(user.id, "research_points", p.research_points + 500.0)
        await query.answer("Научные очки пополнены на +500!")
        return await handle_country_callbacks(update, context)

    elif data == "edit_custom_stat_prompt":
        await query.answer()
        context.user_data["awaiting_stat_edit"] = True
        await query.edit_message_text(
            "⚙️ **РУЧНОЙ ВВОД ПАРАМЕТРА СТРАНЫ:**\n\n"
            "Отправьте сообщение в формате:\n"
            "`<ключ_параметра> <новое_значение>`\n\n"
            "Примеры:\n"
            "• `gdp_billions 3500`\n"
            "• `treasury_billions 800`\n"
            "• `army_divisions 150`\n"
            "• `nuclear_warheads 2500`\n"
            "• `stability 95`\n"
            "• `gps_jamming_active True`\n"
            "• `internet_status FULL_SHUTDOWN`\n"
            "• `tax_rate_corporate 15`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏛️ Отмена", callback_data="menu_stat_editor")]])
        )
        return True

    return False
