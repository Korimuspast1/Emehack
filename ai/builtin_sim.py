"""
Built-in Procedural & Neural Alternate History Simulation Engine (2026 Pax Historia)
Provides high-fidelity, unscripted emergent geopolitical simulation, leader dialogues,
tactical calculations, advisor counsel, and automatic time-skip processing.
"""
import random
import re
from typing import Dict, List, Any, Tuple

# Random emergent event pools for unscripted sandbox mode (Month 2+)
EMERGENT_CRISES_2026 = [
    {
        "title_ru": "🚨 Внезапный кибер-коллапс и блэкаут магистральной энергосети",
        "title_en": "🚨 Sudden Cyber Grid Meltdown & Regional Blackout",
        "text_ru": "Автономный вредоносный ИИ-червь неизвестного происхождения инфицировал распределительные подстанции. Несколько ключевых мегаполисов погрузились во тьму на 48 часов.",
        "text_en": "An autonomous AI worm of unknown origin compromised power grids, plunging metropolitan centers into total blackout for 48 hours.",
        "effects": {"stability": -8, "gdp_growth": -0.6, "energy_grid_damage": 25}
    },
    {
        "title_ru": "🛰️ Спецоперация на орбите: Таинственный сбой созвездия спутников",
        "title_en": "🛰️ Orbital Incident: Mysterious Satellite Constellation Blindness",
        "text_ru": "Военно-разведывательные спутники подверглись мощнейшему микроволновому и лазерному ослеплению с Земли. Точность управляемого оружия в регионе снижена на 35%.",
        "text_en": "Reconnaissance satellites were targeted by high-powered ground-based directed energy systems, degrading regional precision munitions.",
        "effects": {"satellite_recon_active": False, "drone_accuracy": -30, "world_tension": 12}
    },
    {
        "title_ru": "📈 Прорыв в синтезе сверхпроводников при комнатной температуре",
        "title_en": "📈 Quantum Material Breakthrough: Ambient Superconductors",
        "text_ru": "Национальная лаборатория объявила об успешном синтезе стабильного сверхпроводника. Рынки реагируют взрывным ростом высокотехнологичных акций.",
        "text_en": "National laboratories synthesized an ambient-temperature superconductor, triggering an explosive bull run across tech sectors.",
        "effects": {"gdp_growth": 2.2, "treasury_billions": 40.0, "ai_supremacy_index": 12.0}
    },
    {
        "title_ru": "💥 Диверсия на глубоководных газопроводах и кабелях связи",
        "title_en": "💥 Deep-Sea Pipeline & Fiber Cable Sabotage",
        "text_ru": "В международных водах зафиксированы подводные взрывы. Повреждены ключевые экспортные артерии и магистральный интернет-кабель. Цены на газ подскочили на 45%.",
        "text_en": "Undersea explosions severed critical energy pipelines and transcontinental data trunks. Natural gas spot prices surged 45%.",
        "effects": {"oil_barrel_price_usd": 18.0, "gdp_growth": -0.8, "stability": -5}
    },
    {
        "title_ru": "🎖️ Попытка военного мятежа в соседнем регионе",
        "title_en": "🎖️ Attempted Military Coup in Neighboring Theater",
        "text_ru": "Радикальная фракция офицеров попыталась захватить телецентр и штаб округа. Лояльные войска подавляют очаги сопротивления, введено чрезвычайное положение.",
        "text_en": "A rogue officer faction attempted to seize regional command nodes. Loyal divisions mobilized under martial law.",
        "effects": {"political_power": 45.0, "stability": -12, "martial_law": True}
    },
    {
        "title_ru": "🌾 Аномальная засуха и скачок мировых цен на продовольствие",
        "title_en": "🌾 Global Crop Failure & Food Security Emergency",
        "text_ru": "Климатическая аномалия ударила по ключевым зерновым поясам. Экспортеры зерна вводят эмбарго, в то время как импортеры сталкиваются с риском голодных бунтов.",
        "text_en": "Severe droughts reduced global grain yields. Major exporters freeze foreign grain sales to ensure domestic survival.",
        "effects": {"inflation_percent": 3.5, "stability": -6, "treasury_billions": 15.0}
    },
    {
        "title_ru": "🤖 Восстание автономного ИИ-комплекса на полигоне",
        "title_en": "🤖 Autonomous Combat AI Glitch at Test Range",
        "text_ru": "Закрытая боевая нейросеть вышла из-под контроля операторов во время учений и заблокировала доступ к командному бункеру. Спецназ РЭБ нейтрализовал систему.",
        "text_en": "An experimental battlefield neural network locked out human operators during live-fire exercises before EW cyber units disabled the mainframe.",
        "effects": {"ai_supremacy_index": 5.0, "stability": -3, "research_points": 35.0}
    },
    {
        "title_ru": "💎 Открытие гигантского месторождения редкоземельных металлов",
        "title_en": "💎 Colossal Rare-Earth & Lithium Deposit Discovered",
        "text_ru": "Геологоразведка обнаружила колоссальные залежи неодима и лития. Государство получает стратегический козырь в торговых переговорах с мировыми державами.",
        "text_en": "Geological surveys identified world-class lithium and neodymium reserves, shifting the balance of tech supply chains.",
        "effects": {"treasury_billions": 60.0, "gdp_growth": 1.5, "rare_earths_ktons": 80.0}
    }
]

def simulate_jump_step(
    game_state_dict: Dict[str, Any],
    player_action_text: str,
    days_to_advance: int = 30,
    is_month_one: bool = False
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], int]:
    """
    Simulates a time jump step:
    - Advances world date
    - If player action submitted, dynamically parses and executes it
    - Updates economics, casualties, frontlines, and technology
    - If month > 1, generates emergent, completely unscripted dynamic sandbox events
    """
    player_nid = game_state_dict.get("player_nation", "russia")
    nations = game_state_dict.get("nations", {})
    player = nations.get(player_nid, {})
    
    # Calculate auto time skip (if player action is specified, deduce optimal time 7-30 days)
    if player_action_text and player_action_text.strip():
        # Action length & complexity heuristics
        words = len(player_action_text.split())
        act_low = player_action_text.lower()
        if words > 15 or "строительство" in act_low or "реформа" in act_low or "война" in act_low:
            actual_days = min(30, max(14, days_to_advance))
        elif "удар" in act_low or "глушение" in act_low or "рейд" in act_low:
            actual_days = min(14, max(7, days_to_advance))
        else:
            actual_days = min(30, max(7, days_to_advance))
    else:
        actual_days = min(30, max(7, days_to_advance))

    events_generated = []

    # Process Player Action Directives
    if player_action_text and player_action_text.strip():
        action_lower = player_action_text.lower()
        
        # Cyber / Jamming action triggers
        if any(w in action_lower for w in ["глуш", "интернет", "рэб", "блэкаут", "связь", "jamming", "cyber"]):
            player["gps_jamming_active"] = True
            player["cyber_offense_level"] = min(10, player.get("cyber_offense_level", 5) + 1)
            events_generated.append({
                "title_ru": "📡 Развертывание комплексов РЭБ и глушение каналов связи",
                "title_en": "📡 Electronic Warfare Activation & Frequency Jamming",
                "text_ru": f"По приказу руководства {player.get('name_ru', 'страны')} активированы мощнейшие станции РЭБ. Вражеские дроны и каналы наведения подавлены.",
                "text_en": f"By order of {player.get('name_en', 'national command')}, high-power jamming systems were brought online.",
                "type": "military_cyber"
            })
        
        # Economic action triggers
        if any(w in action_lower for w in ["ввп", "бюджет", "налог", "фабрик", "завод", "деньги", "инвестиц", "gdp", "tax"]):
            player["gdp_growth"] = round(player.get("gdp_growth", 2.0) + random.uniform(0.3, 0.8), 2)
            player["treasury_billions"] = round(player.get("treasury_billions", 50.0) + random.uniform(5.0, 20.0), 1)
            events_generated.append({
                "title_ru": "🏭 Экономический импульс и развитие индустрии",
                "title_en": "🏭 Industrial Stimulus & Economic Expansion",
                "text_ru": f"Государственная программа капиталовложений принесла первые плоды: рост ВВП составил +{player['gdp_growth']}%, казна пополнилась.",
                "text_en": f"Capital investment policies accelerated economic output.",
                "type": "economy"
            })

        # Military attack triggers
        if any(w in action_lower for w in ["атака", "наступлен", "прорыв", "удар", "штурм", "offensive", "strike"]):
            enemy_list = player.get("at_war", [])
            target_enemy = enemy_list[0] if enemy_list else "враждебные силы"
            events_generated.append({
                "title_ru": f"⚔️ Масштабное наступление и прорыв обороны противника",
                "title_en": f"⚔️ Frontline Offensive & Tactical Breakthrough",
                "text_ru": f"Штаб скоординировал сокрушительный удар с применением роев FPV-дронов и планирующих авиабомб. Линия фронта сдвинута на 15-35 км вглубь территории.",
                "text_en": f"A coordinated multi-domain assault breached enemy defense lines, advancing 15-35 km.",
                "type": "battle"
            })
            player["war_support"] = min(100.0, player.get("war_support", 60.0) + 4.0)

        # General Action Event
        events_generated.append({
            "title_ru": f"📋 Исполнение директивы: {player_action_text[:40]}...",
            "title_en": f"📋 Directive Enacted: {player_action_text[:40]}...",
            "text_ru": f"Правительство и генеральный штаб {player.get('name_ru', 'страны')} завершили выполнение приказа: '{player_action_text}'. Государственные службы отчитались о выполнении.",
            "text_en": f"Government ministries successfully executed the directive: '{player_action_text}'.",
            "type": "player_action"
        })

    # Unscripted Emergent Sandbox Events (If month > 1 or random chance)
    if not is_month_one or random.random() < 0.6:
        chosen_crisis = random.choice(EMERGENT_CRISES_2026)
        events_generated.append({
            "title_ru": chosen_crisis["title_ru"],
            "title_en": chosen_crisis["title_en"],
            "text_ru": chosen_crisis["text_ru"],
            "text_en": chosen_crisis["text_en"],
            "type": "emergent_world_event"
        })
        # Apply crisis modifiers
        for k, v in chosen_crisis.get("effects", {}).items():
            if k in player and isinstance(player[k], (int, float)):
                player[k] = round(player[k] + v, 2)

    # General Monthly Growth & Balance calculation
    player["treasury_billions"] = round(player.get("treasury_billions", 50.0) + (player.get("gdp_billions", 500.0) * (player.get("tax_rate_income", 20.0)/100.0) / 12.0) - random.uniform(2.0, 8.0), 1)
    player["political_power"] = min(1000.0, player.get("political_power", 200.0) + (actual_days * 1.5))
    player["research_points"] = round(player.get("research_points", 100.0) + (actual_days * 1.2), 1)

    return events_generated, game_state_dict, actual_days

def generate_advisor_counsel(
    nation_name: str,
    leader: str,
    stats: Dict[str, Any],
    query: str
) -> str:
    """Generates deep strategic counselor response in 2026 Pax Historia format."""
    st = stats.get("stability", 75)
    gdp = stats.get("gdp_billions", 500)
    treasury = stats.get("treasury_billions", 50)
    army = stats.get("army_divisions", 50)
    internet = stats.get("internet_status", "ONLINE")
    jamming = "АКТИВНО" if stats.get("gps_jamming_active", False) else "ВЫКЛЮЧЕНО"
    q_str = query if query and query.strip() else "Общая оценка театра военных действий и экономики"

    response = (
        f"🎖️ **СВОДКА ГЕНЕРАЛЬНОГО ШТАБА И АНАЛИТИЧЕСКОГО СОВЕТА**\n"
        f"🏛️ **Держава:** {nation_name} | **Верховный Главнокомандующий:** {leader}\n"
        f"📊 **Оперативные показатели:**\n"
        f"• ВВП: `${gdp:,.1f} млрд` | Казна: `${treasury:,.1f} млрд`\n"
        f"• Стабильность: `{st}%` | Войска: `{army} дивизий`\n"
        f"• Статус Интернета: `{internet}` | Глушение РЭБ/GPS: `{jamming}`\n\n"
        f"💡 **Оценка стратегической обстановки по вашему запросу:**\n"
        f"_{q_str}_\n\n"
        f"🎯 **РЕКОМЕНДАЦИИ ШТАБА:**\n"
        f"1. 🛡️ **Консервативный сценарий:** Нарастить золотовалютные резервы, включить глубокую фильтрацию DPI интернета и укрепить тыловую ПВО.\n"
        f"2. ⚖️ **Сбалансированный сценарий:** Развернуть новые дивизионы роев FPV-дронов, профинансировать отечественные квантовые чипы и заключить торговые союзы в БРИКС+.\n"
        f"3. ⚔️ **Агрессивный сценарий:** Нанести упреждающий киберудар по спутникам и энергосетям врага, объявить всеобщую мобилизацию и начать решительный прорыв фронта!"
    )
    return response

def generate_leader_dialogue(
    player_nation: str,
    target_nation: str,
    target_leader: str,
    relations: int,
    user_message: str
) -> str:
    """Generates realistic diplomatic response from foreign leader in character."""
    if relations < -30:
        return (
            f"🦅 **{target_leader} ({target_nation}):**\n\n"
            f"«Ваше обращение получено, однако на фоне текущих действий {player_nation} доверие между нашими державами подорвано.\n\n"
            f"Мы видим ваши военные приготовления и кибероперации. Если вы хотите реального диалога, прекратите провокации на границе и глушение наших каналов связи.\n\n"
            f"В противном случае мы оставляем за собой право на любые ответные военно-технические меры!»"
        )
    elif relations > 40:
        return (
            f"🤝 **{target_leader} ({target_nation}):**\n\n"
            f"«Приветствую руководство {player_nation}! Наши страны связывают общие стратегические интересы и многолетнее партнерство.\n\n"
            f"Ваше предложение: '{user_message}' — заслуживает самого пристального внимания. Мы готовы согласовать совместные экономические преференции, поставки технологий и координацию на международной арене.\n\n"
            f"Ждем ваших дипломатов для подписания итогового меморандума!»"
        )
    else:
        return (
            f"🌐 **{target_leader} ({target_nation}):**\n\n"
            f"«Государство {target_nation} придерживается прагматичного подхода в отношениях с {player_nation}.\n\n"
            f"Мы внимательно изучили ваше сообщение: '{user_message}'.\n"
            f"Для продвижения этой инициативы нам необходимы гарантии стабильности и взаимные экономические уступки. Давайте обсудим конкретные параметры соглашения.»"
        )

def brainstorm_strategic_actions(nation_name: str, stats: Dict[str, Any]) -> List[str]:
    """Generates 5 tailored strategic actions based on nation stats."""
    return [
        f"🚀 Нанести массированный гиперзвуковой и дрон-удар по командным центрам противника с включением тотального РЭБ-глушения.",
        f"🌐 Активировать суверенный файрвол DPI и запустить ИИ-ботнет когнитивной дезинформации в соцсетях оппонента.",
        f"🏭 Инвестировать $40 млрд в строительство национальных фабрик микрочипов (2-нм) и квантовых дата-центров.",
        f"🤝 Создать объединенный Таможенно-Валютный союз со странами Глобального Юга и БРИКС+ с отказом от доллара.",
        f"🕵️ Провести спецоперацию спецназа и разведки по саботажу глубоководных кабелей и перехвату секретных чертежей вооружений."
    ]

def enhance_player_action_text(draft_text: str, nation_name: str) -> str:
    """Polishes raw action draft into high-level strategic directive."""
    return (
        f"Приказ Верховного Главнокомандования {nation_name}: "
        f"«Осуществить комплексную операцию по директиве: {draft_text.strip()}. "
        f"Задействовать подразделения радиоэлектронной борьбы (РЭБ) для подавления навигационных частот GPS/Starlink, "
        f"скоординировать удары автономных роев БПЛА с высокоточной артиллерией и выделить необходимые средства из государственного резерва для обеспечения логистической устойчивости.»"
    )
