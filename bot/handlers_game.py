"""
Telegram Bot Handlers - Game Loop, Auto-Skip Actions, Jump, Rewind, Saves
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database
from game.engine import (
    get_or_load_session, submit_action_and_auto_skip, manual_time_jump, rewind_turns
)
from ai.engine import AIEngine
from config import TIME_STEPS

async def cmd_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /action <text> command with automatic time advancement."""
    user = update.effective_user
    action_text = " ".join(context.args) if context.args else ""
    if not action_text:
        await update.message.reply_text(
            "✍️ **Напишите ваш приказ или промпт:**\n"
            "Пример: `/action Развернуть комплексы РЭБ для глушения спутников и начать наступление`\n\n"
            "Или просто напишите сообщение боту в свободном формате!",
            parse_mode="Markdown"
        )
        return

    msg = await update.message.reply_text("⏳ **ИИ обрабатывает приказ и моделирует ход симуляции (авто-скип)...**", parse_mode="Markdown")

    events, session, days_advanced = await submit_action_and_auto_skip(user.id, action_text)
    p_nation = session.player_nation

    report_text = (
        f"⚡ **ПРИКАЗ ВЫПОЛНЕН! ВРЕМЯ ПРОДВИНУТО НА {days_advanced} ДНЕЙ**\n"
        f"📅 **Новая дата:** `{session.get_date_str()}` | **Ход:** `#{session.turn_count}`\n\n"
        f"📊 **Показатели {p_nation.name_ru}:**\n"
        f"• ВВП: `${p_nation.gdp_billions:,.1f}B` | Казна: `${p_nation.treasury_billions:,.1f}B`\n"
        f"• Стабильность: `{p_nation.stability:.0f}%` | Армия: `{p_nation.army_divisions} див.`\n"
        f"• РЭБ/Глушение: `{'АКТИВНО 🛰️' if p_nation.gps_jamming_active else 'ВЫКЛ 🟢'}`\n\n"
        f"📰 **СВОДКА СОБЫТИЙ:**\n"
    )

    for ev in events:
        report_text += f"\n• **{ev.get('title_ru', 'Событие')}**\n{ev.get('text_ru', '')}\n"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗺️ Посмотреть карту", callback_data="menu_map"), InlineKeyboardButton("📝 Следующий приказ", callback_data="game_write_action")],
        [InlineKeyboardButton("🎖️ Советник ИИ", callback_data="menu_advisor"), InlineKeyboardButton("⏪ Откат (Rewind)", callback_data="game_rewind_1")],
        [InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
    ])

    await msg.edit_text(report_text, parse_mode="Markdown", reply_markup=kb)

async def cmd_jump(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /jump command opening time-jump selector."""
    kb = []
    row = []
    for k, v in TIME_STEPS.items():
        row.append(InlineKeyboardButton(v["label_ru"], callback_data=f"jump_step_{k}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    kb.append([InlineKeyboardButton("🏛️ Назад в меню", callback_data="menu_main")])

    await update.message.reply_text(
        "⏳ **ВЫБЕРИТЕ ШАГ ПРОДВИЖЕНИЯ ВРЕМЕНИ (TIME-JUMP):**\n"
        "Мир перейдет в режим нелинейной симуляции, произойдут случайные мировые события и рассчитаются эффекты.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def cmd_rewind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /rewind command."""
    user = update.effective_user
    success, msg_text, _ = rewind_turns(user.id, steps=1)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⏪ Откатить еще на 1 ход", callback_data="game_rewind_1")],
        [InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
    ])
    await update.message.reply_text(f"⏪ **РЕЗУЛЬТАТ ОТКАТА ВРЕМЕНИ:**\n\n{msg_text}", parse_mode="Markdown", reply_markup=kb)

async def handle_game_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Dispatches game-related callback queries."""
    query = update.callback_query
    data = query.data
    user = update.effective_user

    if data == "game_quick_jump":
        await query.answer("Продвигаем время...")
        events, session, days = await manual_time_jump(user.id, "1m")
        p = session.player_nation
        text = (
            f"⚡ **ХОД ПРОДВИНУТ НА {days} ДНЕЙ!**\n"
            f"📅 `{session.get_date_str()}` | **Ход:** `#{session.turn_count}`\n\n"
            f"📊 **Показатели {p.name_ru}:**\n"
            f"• ВВП: `${p.gdp_billions:,.1f}B` | Казна: `${p.treasury_billions:,.1f}B`\n"
            f"• Стабильность: `{p.stability:.0f}%` | РЭБ: `{'АКТИВНО 🛰️' if p.gps_jamming_active else 'ВЫКЛ 🟢'}`\n\n"
            f"📰 **НОВОСТИ:**\n"
        )
        for ev in events:
            text += f"\n• **{ev.get('title_ru', '')}**\n{ev.get('text_ru', '')}\n"

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚡ Еще 1 месяц", callback_data="game_quick_jump"), InlineKeyboardButton("📝 Приказ", callback_data="game_write_action")],
            [InlineKeyboardButton("🗺️ Карта", callback_data="menu_map"), InlineKeyboardButton("⏪ Откат", callback_data="game_rewind_1")],
            [InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        return True

    elif data.startswith("jump_step_"):
        step = data.replace("jump_step_", "")
        await query.answer("Симуляция времени...")
        events, session, days = await manual_time_jump(user.id, step)
        text = f"⏳ **ВРЕМЯ ПРОДВИНУТО НА {days} ДНЕЙ!**\n📅 `{session.get_date_str()}`\n\n"
        for ev in events:
            text += f"• **{ev.get('title_ru', '')}**\n{ev.get('text_ru', '')}\n\n"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗺️ Карта", callback_data="menu_map"), InlineKeyboardButton("🏛️ Меню", callback_data="menu_main")]
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        return True

    elif data == "game_write_action":
        await query.answer()
        context.user_data["awaiting_action"] = True
        await query.edit_message_text(
            "✍️ **РЕЖИМ ВВОДА ПРИКАЗА ВЕРХОВНОГО ГЛАВНОКОМАНДУЮЩЕГО:**\n\n"
            "Напишите любой приказ, закон или стратегию в ответном сообщении.\n"
            "ИИ автоматически исполнит его, пересчитает параметры и продвинет время (до 1 месяца)!\n\n"
            "Примеры:\n"
            "• _«Включить тотальное глушение интернета и GPS в приграничной зоне, направить $25 млрд на квантовые микрочипы»_\n"
            "• _«Начать массированное наступление бронетанковых клиньев при поддержке 50 000 FPV-дронов»_\n"
            "• _«Снизить налоги для населения и заключить военный альянс с Китаем и Индией»_",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏛️ Отмена / Назад", callback_data="menu_main")]])
        )
        return True

    elif data == "game_rewind_menu" or data == "game_rewind_1":
        await query.answer()
        success, msg_text, _ = rewind_turns(user.id, steps=1)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⏪ Откатить еще на 1 ход", callback_data="game_rewind_1")],
            [InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
        ])
        await query.edit_message_text(f"⏪ **РЕЗУЛЬТАТ ОТКАТА ВРЕМЕНИ:**\n\n{msg_text}", parse_mode="Markdown", reply_markup=kb)
        return True

    return False
