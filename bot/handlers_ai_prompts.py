"""
Telegram Bot Handlers - Custom AI Integration (BYOK) & System Prompt Editor
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database
from config import SUPPORTED_PROVIDERS, DEFAULT_MODELS, PROMPT_CATEGORIES
from ai.prompt_manager import get_default_prompt

async def cmd_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /ai command."""
    user = update.effective_user
    u_data = database.get_or_create_user(user.id)

    provider = u_data.get("ai_provider", "builtin")
    model = u_data.get("ai_model", "builtin-pro-neural-2026")
    has_key = "Установлен ✅" if u_data.get("ai_api_key") else "Не требуется (Встроенный ИИ) 🟢"

    kb = [
        [InlineKeyboardButton("🧠 Встроенный нейросимулятор (Default)", callback_data="set_ai_provider_builtin")],
        [InlineKeyboardButton("🌐 OpenRouter (Все модели)", callback_data="set_ai_provider_openrouter"), InlineKeyboardButton("⚡ Groq (Llama 3.3 70B)", callback_data="set_ai_provider_groq")],
        [InlineKeyboardButton("🟢 OpenAI (GPT-4o)", callback_data="set_ai_provider_openai"), InlineKeyboardButton("🟣 Anthropic (Claude 3.5)", callback_data="set_ai_provider_anthropic")],
        [InlineKeyboardButton("🔵 DeepSeek API", callback_data="set_ai_provider_deepseek"), InlineKeyboardButton("💻 Ollama (Local LLM)", callback_data="set_ai_provider_ollama")],
        [InlineKeyboardButton("🔗 Свой Custom HTTP API", callback_data="set_ai_provider_custom")],
        [InlineKeyboardButton("🔑 Ввести / Изменить API Ключ", callback_data="prompt_input_api_key")],
        [InlineKeyboardButton("⚙️ Изменить имя модели (Model ID)", callback_data="prompt_input_model_id")],
        [InlineKeyboardButton("📜 Редактор системных промптов", callback_data="menu_prompts_editor")],
        [InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
    ]

    text = (
        f"🤖 **ЦЕНТР УПРАВЛЕНИЯ ИИ И ПОДКЛЮЧЕНИЯ МОДЕЛЕЙ (BYOK)**\n\n"
        f"Текущий активный провайдер: `{provider.upper()}`\n"
        f"Модель: `{model}`\n"
        f"Статус API ключа: `{has_key}`\n"
        f"Температура: `{u_data.get('ai_temperature', 0.7)}`\n\n"
        f"Вы можете выбрать встроенный офлайн-симулятор или подключить любой внешний ИИ со своим API-ключом:"
    )

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def cmd_prompts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /prompts command."""
    user = update.effective_user
    buttons = []
    for pcat in PROMPT_CATEGORIES:
        buttons.append([InlineKeyboardButton(f"📜 {pcat}", callback_data=f"view_prompt_{pcat}")])
    buttons.append([InlineKeyboardButton("🔄 Сбросить все промпты к дефолту", callback_data="reset_all_prompts")])
    buttons.append([InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")])

    text = (
        "📜 **РЕДАКТОР СИСТЕМНЫХ ПРОМПТОВ PAX HISTORIA (12 КАТЕГОРИЙ)**\n\n"
        "Вы можете кастомизировать любой промпт симулятора, используя переменные:\n"
        "`{NATION}`, `{YEAR}`, `{DATE}`, `{LEADER}`, `{IDEOLOGY}`, `{STABILITY}`, `{GDP}`, `{TREASURY}`, "
        "`{ARMY_DIVISIONS}`, `{INTERNET_STATUS}`, `{GPS_JAMMING}`, `{WARS}`, `{ALLIES}`, `{PLAYER_ACTION}`.\n\n"
        "Выберите категорию для просмотра и редактирования:"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

async def handle_ai_prompts_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Dispatches AI provider switcher and prompt editor callback queries."""
    query = update.callback_query
    data = query.data
    user = update.effective_user

    if data == "menu_ai_settings":
        await query.answer()
        u_data = database.get_or_create_user(user.id)
        provider = u_data.get("ai_provider", "builtin")
        model = u_data.get("ai_model", "builtin-pro-neural-2026")
        has_key = "Установлен ✅" if u_data.get("ai_api_key") else "Не требуется (Встроенный ИИ) 🟢"

        kb = [
            [InlineKeyboardButton("🧠 Встроенный нейросимулятор", callback_data="set_ai_provider_builtin")],
            [InlineKeyboardButton("🌐 OpenRouter", callback_data="set_ai_provider_openrouter"), InlineKeyboardButton("⚡ Groq", callback_data="set_ai_provider_groq")],
            [InlineKeyboardButton("🟢 OpenAI", callback_data="set_ai_provider_openai"), InlineKeyboardButton("🟣 Anthropic", callback_data="set_ai_provider_anthropic")],
            [InlineKeyboardButton("🔵 DeepSeek", callback_data="set_ai_provider_deepseek"), InlineKeyboardButton("💻 Ollama", callback_data="set_ai_provider_ollama")],
            [InlineKeyboardButton("🔗 Custom API", callback_data="set_ai_provider_custom")],
            [InlineKeyboardButton("🔑 Ввести API Ключ", callback_data="prompt_input_api_key"), InlineKeyboardButton("⚙️ Имя модели", callback_data="prompt_input_model_id")],
            [InlineKeyboardButton("📜 Редактор промптов", callback_data="menu_prompts_editor")],
            [InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")]
        ]
        text = (
            f"🤖 **НАСТРОЙКИ ИИ (BYOK)**\n\n"
            f"Провайдер: `{provider.upper()}` | Модель: `{model}`\n"
            f"API Ключ: `{has_key}`\n\n"
            f"Выберите провайдер:"
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
        return True

    elif data.startswith("set_ai_provider_"):
        prov = data.replace("set_ai_provider_", "")
        def_model = DEFAULT_MODELS.get(prov, "default-model")
        database.update_user_settings(user.id, ai_provider=prov, ai_model=def_model)
        await query.answer(f"Провайдер переключен на: {prov.upper()}!")
        return await handle_ai_prompts_callbacks(update, context)

    elif data == "prompt_input_api_key":
        await query.answer()
        context.user_data["awaiting_api_key"] = True
        await query.edit_message_text(
            "🔑 **ВВЕДИТЕ ВАШ API КЛЮЧ:**\n\n"
            "Отправьте ваш API ключ от выбранного провайдера (OpenRouter, OpenAI, Groq, Anthropic, DeepSeek) в ответном сообщении.\n"
            "Ключ сохраняется в защищенной базе SQLite.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏛️ Отмена", callback_data="menu_ai_settings")]])
        )
        return True

    elif data == "prompt_input_model_id":
        await query.answer()
        context.user_data["awaiting_model_id"] = True
        await query.edit_message_text(
            "⚙️ **ВВЕДИТЕ ИМЯ МОДЕЛИ (MODEL ID):**\n\n"
            "Примеры:\n"
            "• `google/gemini-2.0-flash-001`\n"
            "• `gpt-4o-mini`\n"
            "• `claude-3-5-sonnet-20241022`\n"
            "• `llama-3.3-70b-versatile`\n"
            "• `deepseek-chat`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏛️ Отмена", callback_data="menu_ai_settings")]])
        )
        return True

    elif data == "menu_prompts_editor":
        await query.answer()
        buttons = []
        for pcat in PROMPT_CATEGORIES:
            buttons.append([InlineKeyboardButton(f"📜 {pcat}", callback_data=f"view_prompt_{pcat}")])
        buttons.append([InlineKeyboardButton("🔄 Сбросить все промпты к дефолту", callback_data="reset_all_prompts")])
        buttons.append([InlineKeyboardButton("🏛️ Главное меню", callback_data="menu_main")])

        text = "📜 **РЕДАКТОР ПРОМПТОВ:**\n\nВыберите категорию для просмотра и изменения:"
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))
        return True

    elif data.startswith("view_prompt_"):
        pcat = data.replace("view_prompt_", "")
        await query.answer()
        user_prompts = database.get_user_custom_prompts(user.id)
        current_text = user_prompts.get(pcat, get_default_prompt(pcat))

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✍️ Редактировать этот промпт", callback_data=f"edit_prompt_{pcat}")],
            [InlineKeyboardButton("🔄 Сбросить к исходному", callback_data=f"reset_prompt_{pcat}")],
            [InlineKeyboardButton("📜 Назад к списку промптов", callback_data="menu_prompts_editor")]
        ])
        await query.edit_message_text(
            f"📜 **ПРОМПТ: `{pcat}`**\n\n```\n{current_text}\n```",
            parse_mode="Markdown",
            reply_markup=kb
        )
        return True

    elif data.startswith("edit_prompt_"):
        pcat = data.replace("edit_prompt_", "")
        await query.answer()
        context.user_data["awaiting_prompt_text"] = pcat
        await query.edit_message_text(
            f"✍️ **РЕДАКТИРОВАНИЕ ПРОМПТА `{pcat}`:**\n\n"
            f"Отправьте новый текст системного промпта в ответном сообщении.\n"
            f"Вы можете использовать переменные: `{{NATION}}`, `{{YEAR}}`, `{{LEADER}}`, `{{STABILITY}}`, `{{GDP}}`, `{{TREASURY}}`, `{{INTERNET_STATUS}}`, `{{PLAYER_ACTION}}`.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏛️ Отмена", callback_data=f"view_prompt_{pcat}")]])
        )
        return True

    elif data.startswith("reset_prompt_"):
        pcat = data.replace("reset_prompt_", "")
        database.reset_user_custom_prompt(user.id, pcat)
        await query.answer(f"Промпт {pcat} сброшен к дефолту!")
        return await handle_ai_prompts_callbacks(update, context)

    elif data == "reset_all_prompts":
        database.reset_user_custom_prompt(user.id)
        await query.answer("Все промпты сброшены к дефолту!")
        return await handle_ai_prompts_callbacks(update, context)

    return False
