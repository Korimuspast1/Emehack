"""
Telegram Bot Handlers - Strategic AI Advisor & Counsel
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from game.engine import get_or_load_session
from ai.engine import AIEngine

async def cmd_advisor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /advisor command."""
    user = update.effective_user
    query_text = " ".join(context.args) if context.args else ""
    session = get_or_load_session(user.id)
    p = session.player_nation

    if query_text:
        msg = await update.message.reply_text("🎖️ **Аналитический штаб готовит стратегический ответ...**", parse_mode="Markdown")
        response = await AIEngine.consult_advisor(
            user_id=user.id,
            nation_name=p.name_ru,
            leader=p.leader,
            stats=p.to_dict(),
            query=query_text
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💡 Сгенерировать 5 идей (Брейншторм)", callback_data="advisor_brainstorm")],
            [InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
        ])
        await msg.edit_text(response, parse_mode="Markdown", reply_markup=kb)
        return

    # Interactive Advisor Menu
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ Военная оценка и фронты", callback_data="advisor_topic_military")],
        [InlineKeyboardButton("🏭 Экономический прогноз и бюджет", callback_data="advisor_topic_economy")],
        [InlineKeyboardButton("🌐 Оценка РЭБ, глушения и киберугроз", callback_data="advisor_topic_cyber")],
        [InlineKeyboardButton("💡 5 Стратегических идей (Brainstorm)", callback_data="advisor_brainstorm")],
        [InlineKeyboardButton("✍️ Задать свой вопрос советнику", callback_data="advisor_custom_prompt")],
        [InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
    ])

    await update.message.reply_text(
        f"🎖️ **СТРАТЕГИЧЕСКИЙ ИИ-СОВЕТНИК ДЕРЖАВЫ {p.name_ru.upper()}**\n\n"
        f"Приветствую, верховный главнокомандующий **{p.leader}**!\n"
        f"Аналитический совет готов предоставить разведывательную оценку текущей обстановки, "
        f"предложить контрмеры и смоделировать развитие кризиса.\n\n"
        f"Выберите направление для анализа или задайте прямой вопрос:",
        parse_mode="Markdown",
        reply_markup=kb
    )

async def handle_advisor_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Dispatches advisor queries and topic buttons."""
    query = update.callback_query
    data = query.data
    user = update.effective_user
    session = get_or_load_session(user.id)
    p = session.player_nation

    if data == "menu_advisor":
        await query.answer()
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚔️ Военная оценка", callback_data="advisor_topic_military"), InlineKeyboardButton("🏭 Экономика", callback_data="advisor_topic_economy")],
            [InlineKeyboardButton("🌐 РЭБ и Киберугрозы", callback_data="advisor_topic_cyber"), InlineKeyboardButton("💡 5 Идей", callback_data="advisor_brainstorm")],
            [InlineKeyboardButton("✍️ Свой вопрос", callback_data="advisor_custom_prompt")],
            [InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
        ])
        await query.edit_message_text(
            f"🎖️ **СТРАТЕГИЧЕСКИЙ ИИ-СОВЕТНИК ({p.name_ru})**\n\n"
            f"Выберите тему аналитического доклада:",
            parse_mode="Markdown",
            reply_markup=kb
        )
        return True

    elif data.startswith("advisor_topic_"):
        topic = data.replace("advisor_topic_", "")
        topic_queries = {
            "military": "Оценка расстановки сил на фронте, боеспособности армии, запасов ракет и уязвимостей ПВО",
            "economy": "Оценка устойчивости экономики к санкциям, темпов роста ВВП, наполнения казны и дефицита",
            "cyber": "Оценка эффективности систем глушения РЭБ, защиты критических сетей от взломов и космической разведки"
        }
        await query.answer("Штаб анализирует...")
        q_text = topic_queries.get(topic, "Стратегический обзор")
        resp = await AIEngine.consult_advisor(user.id, p.name_ru, p.leader, p.to_dict(), q_text)
        
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💡 5 Стратегических идей", callback_data="advisor_brainstorm")],
            [InlineKeyboardButton("🎖️ Назад к советнику", callback_data="menu_advisor"), InlineKeyboardButton("🏛️ Меню", callback_data="menu_main")]
        ])
        await query.edit_message_text(resp, parse_mode="Markdown", reply_markup=kb)
        return True

    elif data == "advisor_brainstorm":
        await query.answer("Генерируем идеи...")
        ideas = await AIEngine.brainstorm_actions(user.id, p.name_ru, p.to_dict())
        text = f"💡 **5 СТРАТЕГИЧЕСКИХ РЕКОМЕНДАЦИЙ ШТАБА ДЛЯ {p.name_ru.upper()}:**\n\n"
        for idx, idea in enumerate(ideas, 1):
            text += f"**{idx}.** {idea}\n\n"

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✍️ Исполнить приказ", callback_data="game_write_action")],
            [InlineKeyboardButton("🎖️ Назад к советнику", callback_data="menu_advisor"), InlineKeyboardButton("🏛️ Меню", callback_data="menu_main")]
        ])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        return True

    elif data == "advisor_custom_prompt":
        await query.answer()
        context.user_data["awaiting_advisor_prompt"] = True
        await query.edit_message_text(
            "✍️ **ЗАДАЙТЕ ВОПРОС СТРАТЕГИЧЕСКОМУ СОВЕТНИКУ:**\n\n"
            "Напишите любой вопрос о войне, экономике, дипломатии или технологиях в ответном сообщении.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏛️ Отмена", callback_data="menu_advisor")]])
        )
        return True

    return False
