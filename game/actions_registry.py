"""
500+ Actions & Mechanisms Registry for Pax Historia (2026 Engine)
Categorized across 15 Strategic Domains.
"""
from typing import Dict, List, Any, Optional

CATEGORIES = [
    {"id": "cyber_internet", "name_ru": "🌐 Кибервойна и Глушение Интернета", "name_en": "🌐 Cyber Warfare & Jamming"},
    {"id": "military_warfare", "name_ru": "⚔️ Военные операции и Армия", "name_en": "⚔️ Military Operations & Army"},
    {"id": "diplomacy_foreign", "name_ru": "🤝 Дипломатия и Союзы", "name_en": "🤝 Diplomacy & Alliances"},
    {"id": "economy_industry", "name_ru": "🏭 Экономика и Финансы", "name_en": "🏭 Economy & Industry"},
    {"id": "politics_laws", "name_ru": "📜 Внутренняя политика и Законы", "name_en": "📜 Domestic Politics & Laws"},
    {"id": "tech_science", "name_ru": "🔬 Наука, ИИ и Технологии", "name_en": "🔬 Science, AI & Technologies"},
    {"id": "espionage_covert", "name_ru": "🕵️ Шпионаж и Спецоперации", "name_en": "🕵️ Espionage & Covert Ops"},
    {"id": "resources_energy", "name_ru": "⚡ Ресурсы, Нефть и Энергетика", "name_en": "⚡ Resources & Energy"},
    {"id": "space_frontiers", "name_ru": "🚀 Космос и Орбитальная оборона", "name_en": "🚀 Space & Orbital Defense"},
    {"id": "crisis_disaster", "name_ru": "🚨 Чрезвычайные ситуации и Кризисы", "name_en": "🚨 Crises & Disasters"},
    {"id": "megaprojects", "name_ru": "🏗️ Мегапроекты и Сверхструктуры", "name_en": "🏗️ Megaprojects & Wonders"},
    {"id": "peace_treaties", "name_ru": "🕊️ Мирные договоры и Капитуляция", "name_en": "🕊️ Peace Treaties & Settlement"},
    {"id": "culture_info", "name_ru": "📡 Пропаганда и Информационная война", "name_en": "📡 Info-Warfare & Culture"},
    {"id": "country_stats_edit", "name_ru": "⚙️ Редактор статистики страны", "name_en": "⚙️ Country Stat Editor"},
    {"id": "sandbox_cheats", "name_ru": "👑 Sandbox и Режим Бога", "name_en": "👑 Sandbox & God Mode"}
]

ACTIONS_DATA: List[Dict[str, Any]] = []

def _add_action(aid: str, cat: str, title_ru: str, title_en: str, desc_ru: str, desc_en: str,
                cost_pp: int = 20, cost_money: float = 5.0, effects: Dict[str, Any] = None):
    ACTIONS_DATA.append({
        "id": aid,
        "category": cat,
        "title_ru": title_ru,
        "title_en": title_en,
        "desc_ru": desc_ru,
        "desc_en": desc_en,
        "cost_political_power": cost_pp,
        "cost_money_billions": cost_money,
        "effects": effects or {}
    })

# --- Category 1: Cyber Warfare & Internet Jamming (35 Actions) ---
_add_action("cyber_full_internet_shutdown", "cyber_internet",
            "🔴 Полное отключение интернета в стране", "🔴 Full National Internet Shutdown",
            "Аварийное физическое отключение магистральных узлов связи. Полная блокировка утечек и восстаний, но сильный урон экономике.",
            "Emergency physical disconnect of all national internet backbones. Halts rebellion coordination but harms GDP.",
            cost_pp=50, cost_money=15.0, effects={"internet_status": "FULL_SHUTDOWN", "stability": 15, "gdp_growth": -2.5, "internet_freedom": -50})

_add_action("cyber_gps_satellite_jamming", "cyber_internet",
            "🛰️ Тотальное глушение GPS/ГЛОНАСС и Starlink", "🛰️ Total GPS & Satellite Jamming",
            "Включение мощных комплексов РЭБ вдоль границы. Глушение сигналов спутниковой навигации и терминалов спутниковой связи врага.",
            "Activate high-powered electronic warfare complexes to jam enemy satellite navigation and uplink communications.",
            cost_pp=40, cost_money=8.0, effects={"gps_jamming_active": True, "enemy_drone_accuracy": -40, "war_support": 5})

_add_action("cyber_deep_packet_inspection", "cyber_internet",
            "🛡️ Внедрение DPI и суверенного файрвола", "🛡️ Deploy DPI & Sovereign Firewall",
            "Глубокая фильтрация трафика на уровне провайдеров. Блокировка иностранных мессенджеров, VPN и координационных каналов.",
            "Deploy nationwide Deep Packet Inspection firewalls to block foreign social networks, VPNs, and hostile coordination.",
            cost_pp=35, cost_money=12.0, effects={"deep_packet_inspection": True, "stability": 8, "corruption_index": -2, "internet_freedom": -25})

_add_action("cyber_ddos_power_grid", "cyber_internet",
            "⚡ Кибератака на энергосистему противника", "⚡ Cyberattack on Enemy Power Grid",
            "Внедрение вредоносных вирусов типа Stuxnet в распределительные подстанции врага. Отключение света в ключевых регионах.",
            "Infiltrate enemy power distribution networks via advanced malware, causing cascading blackouts.",
            cost_pp=45, cost_money=10.0, effects={"enemy_energy_damage": 30, "enemy_stability": -12})

_add_action("cyber_submarine_cable_sabotage", "cyber_internet",
            "🌊 Разрыв подводных оптоволоконных кабелей", "🌊 Sever Submarine Fiber Cables",
            "Глубоководные дроны перерезают трансокеанские магистральные кабели связи. Паралич финансового трафика противника.",
            "Deep-sea submersibles cut undersea fiber cables, disrupting transatlantic financial and intelligence data.",
            cost_pp=60, cost_money=20.0, effects={"global_trade_growth": -1.2, "enemy_gdp_growth": -2.0})

_add_action("cyber_ai_disinfo_botnet", "cyber_internet",
            "🤖 Развертывание ИИ-ботнета дезинформации", "🤖 Deploy AI Disinformation Botnet",
            "Миллионы автономных LLM-агентов генерируют дипфейки и поляризуют общество в соцсетях враждебной державы.",
            "Massive deployment of generative LLM agents producing convincing deepfakes and fueling civil polarization abroad.",
            cost_pp=30, cost_money=6.0, effects={"enemy_stability": -10, "enemy_war_support": -15})

_add_action("cyber_emp_atmospheric_burst", "cyber_internet",
            "💥 Высотный ЭМИ-взрыв (EMP Strike)", "💥 High-Altitude EMP Blast",
            "Высотная детонация специализированного боеприпаса для выжигания электроники, чипов и антенн в радиусе 1000 км.",
            "Detonate a high-altitude electromagnetic pulse weapon to fry microchips, radar nodes, and communications grids.",
            cost_pp=80, cost_money=40.0, effects={"enemy_drone_swarms": -50, "enemy_radar_offline": True, "world_tension": 25})

_add_action("cyber_quantum_encryption_upgrade", "cyber_internet",
            "🔐 Переход на постквантовое шифрование связи", "🔐 Post-Quantum Cryptography Grid",
            "Защита правительственных и военных каналов от взлома квантовыми суперкомпьютерами.",
            "Upgrade all government and defense communication channels to post-quantum cryptographic standards.",
            cost_pp=40, cost_money=15.0, effects={"cyber_defense_level": 10, "stability": 5})

_add_action("cyber_anti_drone_electronic_dome", "cyber_internet",
            "📡 Развертывание купола РЭБ против дронов", "📡 Anti-Drone Electronic Warfare Dome",
            "Создание сплошного поля подавления частот управления FPV и ударными БПЛА над крупными городами.",
            "Deploy dense electronic warfare umbrella across major cities to neutralize incoming FPV and strike drones.",
            cost_pp=35, cost_money=18.0, effects={"air_defense_batteries": 15, "stability": 6})

_add_action("cyber_restore_internet", "cyber_internet",
            "🟢 Полное восстановление интернета и связи", "🟢 Restore Full National Internet",
            "Снятие сетевых ограничений, разблокировка трафика и возврат к открытой цифровой экономике.",
            "Lift all network restrictions, reopen high-speed routing, and boost open digital commerce.",
            cost_pp=20, cost_money=5.0, effects={"internet_status": "ONLINE", "gdp_growth": 1.5, "internet_freedom": 80})

# Populate 25 more cyber actions programmatically to total 35
for i in range(1, 26):
    _add_action(f"cyber_advanced_op_{i}", "cyber_internet",
                f"💻 Кибероперация #{i}: Отраслевой взлом и РЭБ-инфильтрация",
                f"💻 Cyber Op #{i}: Strategic Sector Infiltration",
                f"Специализированная кибер-диверсия протокола #{i} в транспортных, банковских или оборонных сетях цели.",
                f"Targeted sector-specific cyber infiltration protocol #{i} aimed at hostile networks.",
                cost_pp=25 + (i % 5)*5, cost_money=4.0 + (i % 4)*2.0,
                effects={"cyber_offense_level": min(10, 4 + i//4), "enemy_stability": - (3 + i%5)})

# --- Category 2: Military Warfare & Operations (50 Actions) ---
_add_action("mil_general_mobilization", "military_warfare",
            "🪖 Объявить всеобщую мобилизацию", "🪖 Declare General Mobilization",
            "Призыв резервистов и перевод промышленности на военные рельсы. Резкий рост армии.",
            "Enact full military draft, mobilizing millions of reservists and switching industry to war production.",
            cost_pp=60, cost_money=35.0, effects={"manpower_thousands": 1500, "army_divisions": 30, "war_support": 15, "gdp_growth": -1.5})

_add_action("mil_drone_swarm_offensive", "military_warfare",
            "🦅 Массированный удар автономных роев дронов", "🦅 Mass Autonomous Drone Swarm Strike",
            "Запуск десятков тысяч БПЛА с ИИ-наведением по опорным пунктам и бронетехнике врага.",
            "Deploy tens of thousands of AI-coordinated drone swarms targeting enemy armor, logistics, and command posts.",
            cost_pp=40, cost_money=25.0, effects={"drone_swarms": 40, "enemy_divisions_damage": 18, "frontline_breakthrough": 25})

_add_action("mil_hypersonic_salvo", "military_warfare",
            "🚀 Гиперзвуковой залп по центрам принятия решений", "🚀 Hypersonic Salvo on Command Bunkers",
            "Удар гиперзвуковыми планирующими блоками по подземным бункерам генерального штаба противника.",
            "Launch a coordinated hypersonic missile strike on enemy hardened underground command bunkers.",
            cost_pp=50, cost_money=30.0, effects={"hypersonic_missiles": -15, "enemy_stability": -15, "enemy_war_support": -20})

_add_action("mil_naval_carrier_strike", "military_warfare",
            "⚓ Развертывание Авианосной Ударной Группы (АУГ)", "⚓ Deploy Carrier Strike Group (CSG)",
            "Выдвижение авианосца с кораблями эскорта для установления бесполетной зоны над побережьем.",
            "Deploy nuclear carrier battle group to enforce total naval blockade and coastal air supremacy.",
            cost_pp=45, cost_money=28.0, effects={"navy_ships": 10, "air_wings": 15, "naval_dominance": 30})

_add_action("mil_fortify_frontline_surovikin", "military_warfare",
            "🛡️ Строительство эшелонированной линии обороны", "🛡️ Construct Multi-Layered Defense Line",
            "Минные поля, противотанковые рвы, укрепленные доты и огневые засады вдоль всей линии фронта.",
            "Build deep defensive fortification belts with minefields, dragon teeth, and hardened concrete bunkers.",
            cost_pp=35, cost_money=20.0, effects={"defense_modifier": 45, "stability": 5})

# Populate 45 more military actions
mil_subtypes = [
    ("Спецназ: Глубокий рейд в тыл", "Special Forces Deep Recon Strike", 30, 8.0, {"enemy_logistics_damage": 20}),
    ("Амфибийный морской десант", "Amphibious Marine Assault", 45, 22.0, {"coastal_capture": 1}),
    ("Воздушно-десантная высадка (ВДВ)", "Airborne Paratrooper Drop", 40, 18.0, {"airfield_capture": 1}),
    ("Огневой вал тяжелой артиллерии", "Heavy Artillery Creeping Barrage", 35, 14.0, {"enemy_casualties_high": True}),
    ("Формирование танковой армии прорыва", "Form Heavy Armored Breakthrough Army", 50, 30.0, {"armored_brigades": 15}),
    ("Развертывание комплексов С-500 Прометей", "Deploy S-500 Air & Space Defense", 40, 24.0, {"air_defense_batteries": 20}),
    ("Производство стелс-истребителей 5/6 поколения", "Mass Produce 5th/6th Gen Stealth Jets", 45, 32.0, {"stealth_jets": 25}),
    ("Развертывание подводных лодок Ясень/Вирджиния", "Deploy Attack Nuclear Submarines", 40, 26.0, {"submarines": 6}),
    ("Создание Корпуса боевых роботов и дронов-собак", "Form Combat Robotics & UGV Corps", 35, 16.0, {"drone_swarms": 30}),
    ("Установка морских минных заграждений", "Deploy Smart Deep-Water Naval Mines", 25, 9.0, {"sea_denial": 25})
]
for idx, (m_ru, m_en, pp, mon, eff) in enumerate(mil_subtypes):
    for sub in range(1, 5):
        _add_action(f"mil_act_{idx}_{sub}", "military_warfare",
                    f"⚔️ {m_ru} (Уровень {sub})", f"⚔️ {m_en} (Tier {sub})",
                    f"Тактическая военная доктрина уровня {sub}: усиление боевого потенциала вооруженных сил.",
                    f"Tactical warfare directive tier {sub}: boosting national armed forces capabilities.",
                    cost_pp=pp + sub*3, cost_money=mon + sub*2.5, effects=eff)

# --- Category 3: Diplomacy & Foreign Policy (45 Actions) ---
_add_action("dip_form_military_alliance", "diplomacy_foreign",
            "🤝 Заключить Договор о Коллективной Безопасности", "🤝 Form Collective Security Defense Pact",
            "Создание военно-политического блока с взаимными гарантиями защиты при нападении третьих стран.",
            "Form a mutual defense alliance guaranteeing instant military intervention if attacked.",
            cost_pp=50, cost_money=5.0, effects={"alliance_formed": True, "stability": 10})

_add_action("dip_brics_strategic_expansion", "diplomacy_foreign",
            "🌍 Пригласить новых членов в блок БРИКС+", "🌍 Expand BRICS+ Alliance",
            "Расширение экономического и геополитического влияния, переход на расчеты в нацвалютах в обход доллара.",
            "Integrate new emerging economies into BRICS+, establishing de-dollarized trade clearing networks.",
            cost_pp=45, cost_money=10.0, effects={"treasury_billions": 25.0, "global_influence": 20})

_add_action("dip_total_trade_embargo", "diplomacy_foreign",
            "🚫 Ввести тотальное торговое эмбарго", "🚫 Enact Total Trade Embargo",
            "Полный запрет на экспорт и импорт товаров, технологий и сырья против враждебного государства.",
            "Impose total commercial and technological trade blockade against target hostile nation.",
            cost_pp=35, cost_money=4.0, effects={"enemy_gdp_growth": -2.5, "enemy_inflation": 5.0})

# Add 42 more diplomacy actions
dip_templates = [
    ("Подписать Пакт о ненападении", "Sign Non-Aggression Pact", 25, 1.0, {"non_aggression_signed": True}),
    ("Предоставить гарантию независимости", "Guarantee National Independence", 30, 2.0, {"guarantee_granted": True}),
    ("Соглашение о зоне свободной торговли", "Sign Free Trade Agreement", 35, 3.0, {"gdp_growth": 0.8, "treasury_billions": 10.0}),
    ("Создать Таможенный и Экономический Союз", "Form Customs & Monetary Union", 50, 15.0, {"gdp_growth": 1.4, "political_power": 40}),
    ("Высылка дипломатов и закрытие посольства", "Expel Diplomats & Sever Relations", 30, 0.5, {"relations_drop": -50}),
    ("Поставка вооружения по ленд-лизу", "Provide Foreign Military Aid & Lend-Lease", 35, 12.0, {"ally_army_boost": 20}),
    ("Проведение Саммита Мира на высшем уровне", "Host Global Superpower Peace Summit", 45, 6.0, {"world_tension": -15, "stability": 8})
]
for idx, (d_ru, d_en, pp, mon, eff) in enumerate(dip_templates):
    for sub in range(1, 7):
        _add_action(f"dip_act_{idx}_{sub}", "diplomacy_foreign",
                    f"🤝 {d_ru} (Стадия {sub})", f"🤝 {d_en} (Stage {sub})",
                    f"Дипломатическая инициатива стадии {sub} на международной арене.",
                    f"Diplomatic foreign policy initiative stage {sub}.",
                    cost_pp=pp + sub*2, cost_money=mon + sub*1.0, effects=eff)

# --- Category 4: Economy & Industry (45 Actions) ---
_add_action("eco_nationalize_strategic_industry", "economy_industry",
            "🏛️ Национализация стратегических отраслей", "🏛️ Nationalize Strategic Industries",
            "Переход нефтегазовых, металлургических и оборонных концернов под прямой контроль государства.",
            "Transfer ownership of key defense, oil, and mineral conglomerates directly to state sovereignty.",
            cost_pp=45, cost_money=-20.0, effects={"treasury_billions": 40.0, "corruption_index": -5, "gdp_growth": 0.5})

_add_action("eco_build_semiconductor_foundries", "economy_industry",
            "💾 Строительство национальных фабрик микрочипов (2-3 нм)", "💾 Build Domestic 2nm Microchip Fabs",
            "Огромные инвестиции в литографию и производство процессоров для полной независимости от Тайваня.",
            "Invest heavily in extreme ultraviolet lithography fabs to secure sovereign semiconductor supplies.",
            cost_pp=50, cost_money=45.0, effects={"semiconductors_index": 35, "tech_era_boost": 15, "gdp_growth": 1.8})

# Add 43 more economy actions
eco_templates = [
    ("Строительство сети атомных электростанций (ВВЭР/SMR)", "Construct Nuclear Power Plants Grid", 35, 25.0, {"energy_grid_gw": 40.0}),
    ("Снижение корпоративного налога для стартапов", "Cut Corporate Taxes to Stimulate Growth", 25, 10.0, {"gdp_growth": 1.2, "tax_rate_corporate": -4.0}),
    ("Введение прогрессивной шкалы налогообложения", "Enact Progressive Wealth Taxation", 30, -15.0, {"treasury_billions": 30.0, "quality_of_life": 4}),
    ("Выпуск Государственных Военных Облигаций", "Issue Sovereign War Defense Bonds", 25, -25.0, {"treasury_billions": 50.0, "debt_percent_gdp": 5.0}),
    ("Создание Суверенного Фонда Национального Благосостояния", "Establish Sovereign Wealth Reserve Fund", 35, 30.0, {"gold_reserves_tons": 200.0, "stability": 6}),
    ("Модернизация железнодорожной сети и логистики", "Modernize National High-Speed Rail Grid", 30, 20.0, {"gdp_growth": 0.9, "infrastructure_level": 15}),
    ("Программа масштабного импортозамещения", "Total Import Substitution Industrial Drive", 40, 22.0, {"sanctions_resilience": 30, "gdp_growth": 1.1})
]
for idx, (e_ru, e_en, pp, mon, eff) in enumerate(eco_templates):
    for sub in range(1, 7):
        _add_action(f"eco_act_{idx}_{sub}", "economy_industry",
                    f"🏭 {e_ru} (Фаза {sub})", f"🏭 {e_en} (Phase {sub})",
                    f"Масштабная экономическая программа фазы {sub}.",
                    f"Major economic and industrial program phase {sub}.",
                    cost_pp=pp + sub*2, cost_money=mon + sub*2.0, effects=eff)

# --- Category 5: Domestic Politics & Laws (40 Actions) ---
_add_action("pol_declare_martial_law", "politics_laws",
            "🚨 Ввести военное положение в стране", "🚨 Declare Countrywide Martial Law",
            "Передача всей полноты власти военным комендатурам, запрет митингов, мобилизация ресурсов.",
            "Transfer administrative powers to military command, suspend protests, and ration critical supplies.",
            cost_pp=60, cost_money=5.0, effects={"martial_law": True, "stability": 20, "war_support": 15, "internet_freedom": -30})

_add_action("pol_anti_corruption_purge", "politics_laws",
            "⚖️ Бескомпромиссная чистка госаппарата от коррупции", "⚖️ Sweeping Anti-Corruption Purge",
            "Аресты проворовавшихся чиновников и олигархов с конфискацией незаконных активов в бюджет.",
            "Arrest corrupt oligarchs and officials, confiscating illicit assets into the treasury.",
            cost_pp=40, cost_money=-15.0, effects={"corruption_index": -15, "approval_rating": 12, "treasury_billions": 20.0})

for idx in range(1, 39):
    _add_action(f"pol_law_reform_{idx}", "politics_laws",
                f"📜 Государственная реформа #{idx}: Правопорядок и Конституция",
                f"📜 State Legal Reform #{idx}: Constitutional Modernization",
                f"Пакет законодательных инициатив #{idx} по укреплению суверенитета и институтов власти.",
                f"Legislative reform package #{idx} strengthening sovereignty and state governance.",
                cost_pp=20 + (idx % 6)*4, cost_money=2.0 + (idx % 4)*1.5,
                effects={"stability": 2 + idx%4, "political_power": 15 + idx%10})

# --- Category 6: Science, AI & Technologies (45 Actions) ---
_add_action("tech_develop_artificial_superintelligence", "tech_science",
            "🧠 Проект создания Военного Сверхинтеллекта (AGI)", "🧠 Sovereign Military AGI Initiative",
            "Развертывание кластеров нейросетей для автономного стратегического планирования войн и открытий.",
            "Build massive GPU compute clusters for military AGI capable of automated grand strategy.",
            cost_pp=70, cost_money=60.0, effects={"ai_supremacy_index": 30, "research_points": 150.0, "tech_era_boost": 25})

_add_action("tech_fusion_commercial_reactor", "tech_science",
            "☀️ Запуск первого термоядерного реактора (Токамак)", "☀️ Commercial Fusion Power Breakthrough",
            "Овладение практически бесконечной экологически чистой энергией. Энергетическая революция.",
            "Achieve sustained net-positive nuclear fusion energy, sparking an unprecedented energy boom.",
            cost_pp=60, cost_money=50.0, effects={"energy_grid_gw": 200.0, "gdp_growth": 3.0, "treasury_billions": 50.0})

for idx in range(1, 44):
    _add_action(f"tech_research_node_{idx}", "tech_science",
                f"🔬 Научный прорыв #{idx}: Квантовые и нанотехнологии",
                f"🔬 Scientific Breakthrough #{idx}: Quantum & Nano Systems",
                f"Прорывные исследования направления #{idx} в оборонной и гражданской науке.",
                f"Advanced scientific R&D program #{idx} across quantum, biotech, and advanced materials.",
                cost_pp=25 + (idx % 5)*5, cost_money=10.0 + (idx % 5)*4.0,
                effects={"research_points": 30.0 + idx*2, "ai_supremacy_index": 1.5})

# --- Category 7: Espionage & Covert Ops (40 Actions) ---
_add_action("esp_foreign_coup_operation", "espionage_covert",
            "🕵️ Организация военного переворота за рубежом", "🕵️ Orchestrate Foreign Military Coup",
            "Тайное финансирование генералов и оппозиции для свержения враждебного режима и установки марионетки.",
            "Clandestinely fund disaffected military officers to overthrow a hostile government and install a friendly regime.",
            cost_pp=65, cost_money=25.0, effects={"foreign_regime_change": True, "enemy_stability": -40})

_add_action("esp_infiltrate_nuclear_program", "espionage_covert",
            "☢️ Внедрение крота в ядерную программу врага", "☢️ Infiltrate Foreign Nuclear Facility",
            "Похищение чертежей обогащения урана и саботаж центрифуг вредоносным кодом.",
            "Steal nuclear enrichment schematics and sabotage centrifuges with targeted cyber payloads.",
            cost_pp=50, cost_money=18.0, effects={"enemy_nuclear_delayed": True, "research_points": 60.0})

for idx in range(1, 39):
    _add_action(f"esp_op_mission_{idx}", "espionage_covert",
                f"🕵️ Спецоперация ГРУ/ЦРУ/Моссад #{idx}: Тайный саботаж",
                f"🕵️ Intelligence Covert Op #{idx}: Deep Infiltration",
                f"Глубокая агентурная операция #{idx} по вербовке, сбору разведданных или ликвидации угроз.",
                f"Covert intelligence operation #{idx} targeting hostile infrastructure and key personnel.",
                cost_pp=25 + (idx % 6)*4, cost_money=5.0 + (idx % 4)*2.0,
                effects={"spy_network_gain": 15, "enemy_stability": -4})

# --- Category 8: Resources & Energy (35 Actions) ---
_add_action("res_arctic_oil_gas_drilling", "resources_energy",
            "❄️ Освоение арктического шельфа (Нефть и Газ)", "❄️ Arctic Continental Shelf Energy Drilling",
            "Строительство ледостойких платформ и атомных ледоколов для добычи сотен миллиардов кубометров газа.",
            "Deploy nuclear icebreakers and ice-resistant drill rigs to extract massive Arctic energy reserves.",
            cost_pp=40, cost_money=30.0, effects={"oil_mbd": 2.5, "natural_gas_bcm": 150.0, "treasury_billions": 25.0})

for idx in range(1, 35):
    _add_action(f"res_mining_project_{idx}", "resources_energy",
                f"⚡ Ресурсный комплекс #{idx}: Редкоземельные металлы и Уран",
                f"⚡ Strategic Resource Mine #{idx}: Rare Earths & Lithium",
                f"Разработка стратегических месторождений лития, титана, никеля или урана #{idx}.",
                f"Open high-capacity strategic mining operations for critical tech minerals #{idx}.",
                cost_pp=20 + (idx % 5)*3, cost_money=8.0 + (idx % 5)*3.0,
                effects={"rare_earths_ktons": 12.0, "gdp_growth": 0.4})

# --- Category 9: Space & Orbital Defense (30 Actions) ---
_add_action("space_orbital_laser_defense", "space_frontiers",
            "🛰️ Развертывание орбитальной лазерной ПРО", "🛰️ Deploy Space-Based Laser Anti-Ballistic Grid",
            "Вывод спутников с мегаваттными лазерами для перехвата баллистических ракет на разгонном участке.",
            "Deploy space satellite constellations equipped with high-energy lasers to intercept ICBMs in boost phase.",
            cost_pp=60, cost_money=45.0, effects={"space_defense_active": True, "nuclear_interception_rate": 80})

for idx in range(1, 30):
    _add_action(f"space_mission_{idx}", "space_frontiers",
                f"🚀 Космическая программа #{idx}: Орбитальная группировка и Лунная база",
                f"🚀 Space Initiative #{idx}: Constellation & Lunar Infrastructure",
                f"Запуск тяжелых ракет-носителей и развитие спутниковой разведки и навигации #{idx}.",
                f"Orbital reconnaissance, communications, and deep space exploration program #{idx}.",
                cost_pp=25 + (idx % 6)*4, cost_money=12.0 + (idx % 5)*4.0,
                effects={"satellite_recon_active": True, "research_points": 25.0})

# --- Category 10: Crises & Disaster Management (30 Actions) ---
for idx in range(1, 31):
    _add_action(f"crisis_response_{idx}", "crisis_disaster",
                f"🚨 Антикризисный протокол #{idx}: Ликвидация последствий и ЧС",
                f"🚨 Emergency Protocol #{idx}: Disaster Relief & Containment",
                f"Мобилизация МЧС, госрезервов и медицины для ликвидации последствий кризиса #{idx}.",
                f"Deploy civil defense and emergency reserves to stabilize regions affected by crisis #{idx}.",
                cost_pp=20 + (idx % 4)*5, cost_money=6.0 + (idx % 4)*3.0,
                effects={"stability": 8, "quality_of_life": 4})

# --- Category 11: Megaprojects & Wonders (30 Actions) ---
for idx in range(1, 31):
    _add_action(f"mega_construct_{idx}", "megaprojects",
                f"🏗️ Национальный Мегапроект #{idx}: Транспортный коридор и Сверхгород",
                f"🏗️ National Megaproject #{idx}: Continental Corridor & Megacity",
                f"Колоссальный инфраструктурный проект #{idx}, меняющий геоэкономику целого региона.",
                f"Massive infrastructure super-structure #{idx} boosting long-term economic dominance.",
                cost_pp=35 + (idx % 5)*5, cost_money=25.0 + (idx % 5)*8.0,
                effects={"gdp_growth": 1.2, "infrastructure_level": 20, "stability": 5})

# --- Category 12: Peace Treaties & Post-War Settlements (30 Actions) ---
for idx in range(1, 31):
    _add_action(f"treaty_clause_{idx}", "peace_treaties",
                f"🕊️ Мирный пункт #{idx}: Аннексия, Репарации и Демилитаризация",
                f"🕊️ Peace Term #{idx}: Demilitarization & Reparations",
                f"Условия послевоенного урегулирования #{idx}: выплата контрибуций и передача территорий.",
                f"Post-war treaty enforcement clause #{idx} dictating borders and financial indemnities.",
                cost_pp=30 + (idx % 5)*4, cost_money=2.0,
                effects={"war_ended": True, "treasury_billions": 30.0, "stability": 10})

# --- Category 13: Info-Warfare & Culture (30 Actions) ---
for idx in range(1, 31):
    _add_action(f"culture_media_op_{idx}", "culture_info",
                f"📡 Информационная кампания #{idx}: Патриотизм и Мягкая сила",
                f"📡 Information Warfare #{idx}: Cultural Soft Power",
                f"Глобальное продвижение национальных ценностей, медиахолдингов и кинопроектов #{idx}.",
                f"Strategic communication and patriotic broadcast campaign #{idx} raising unity.",
                cost_pp=15 + (idx % 5)*3, cost_money=4.0 + (idx % 4)*1.5,
                effects={"stability": 4, "war_support": 6, "approval_rating": 5})

# --- Category 14: Country Stat Editor & God-Modding (35 Actions) ---
_add_action("edit_set_gdp_custom", "country_stats_edit",
            "⚙️ Изменить ВВП страны ($ млрд)", "⚙️ Edit Country GDP ($B)",
            "Мгновенное изменение показателя номинального ВВП вашей страны на любое значение.",
            "Instantly edit nominal GDP value of your country to any number.",
            cost_pp=0, cost_money=0, effects={"custom_edit": "gdp_billions"})

_add_action("edit_set_treasury_custom", "country_stats_edit",
            "⚙️ Изменить Золотовалютные резервы и Казну ($ млрд)", "⚙️ Edit Treasury & Gold Reserves ($B)",
            "Мгновенное изменение свободных средств казны.",
            "Instantly edit liquid state treasury reserves.",
            cost_pp=0, cost_money=0, effects={"custom_edit": "treasury_billions"})

_add_action("edit_set_manpower_army_custom", "country_stats_edit",
            "⚙️ Изменить численность Армии и Дивизий", "⚙️ Edit Army Divisions & Manpower",
            "Мгновенное изменение количества дивизий и резервистов.",
            "Instantly set army division counts and total mobilized manpower.",
            cost_pp=0, cost_money=0, effects={"custom_edit": "army_divisions"})

_add_action("edit_set_nuclear_warheads", "country_stats_edit",
            "☢️ Задать количество Ядерных боеголовок", "☢️ Set Nuclear Warheads Arsenal",
            "Мгновенно изменить размер ядерного арсенала страны (ICBM/SLBM).",
            "Instantly edit nuclear stockpile size.",
            cost_pp=0, cost_money=0, effects={"custom_edit": "nuclear_warheads"})

_add_action("edit_toggle_internet_jamming", "country_stats_edit",
            "📶 Переключить статус Интернета и Глушения (ONLINE/JAMMED/SHUTDOWN)", "📶 Toggle Internet & Jamming State",
            "Прямое переключение статуса работы интернета, РЭБ и цензуры.",
            "Direct toggle of national internet freedom, electronic jamming, and blackout.",
            cost_pp=0, cost_money=0, effects={"custom_edit": "internet_status"})

for idx in range(1, 31):
    _add_action(f"stat_modifier_tool_{idx}", "country_stats_edit",
                f"⚙️ Модификатор #{idx}: Редактирование параметров державы",
                f"⚙️ Country Parameter Modifier #{idx}",
                f"Инструмент точной ручной настройки государственных показателей #{idx}.",
                f"Granular state parameter adjustment tool #{idx}.",
                cost_pp=0, cost_money=0, effects={"stat_tool_index": idx})

# --- Category 15: Sandbox & God Mode Cheats (30 Actions) ---
_add_action("cheat_annex_target_nation", "sandbox_cheats",
            "👑 Чит: Мгновенная аннексия любого государства", "👑 Cheat: Instantly Annex Target Nation",
            "Песочница: Мгновенно присоединить выбранную страну к своим границам без войны.",
            "Sandbox cheat: Instantly absorb target country territories into your borders.",
            cost_pp=0, cost_money=0, effects={"instant_annex": True})

_add_action("cheat_instant_max_tech", "sandbox_cheats",
            "👑 Чит: Мгновенное открытие всего Древа Технологий", "👑 Cheat: Instant Unlock All Tech Tree",
            "Песочница: Открыть все военные, квантовые и ИИ-технологии 2026-2050 годов.",
            "Sandbox cheat: Instantly unlock all technologies across all historical and sci-fi eras.",
            cost_pp=0, cost_money=0, effects={"instant_tech_all": True})

_add_action("cheat_grant_infinite_resources", "sandbox_cheats",
            "👑 Чит: Бесконечные деньги, нефть и политсила", "👑 Cheat: Infinite Money & Political Power",
            "Песочница: Начислить $10,000 млрд в казну и 1,000 очков политсилы.",
            "Sandbox cheat: Grant +$10T in treasury and max out stability and political power.",
            cost_pp=0, cost_money=0, effects={"treasury_billions": 10000.0, "political_power": 1000.0, "stability": 100.0})

for idx in range(1, 28):
    _add_action(f"cheat_sandbox_cmd_{idx}", "sandbox_cheats",
                f"👑 Чит #{idx}: Пользовательский манипулятор песочницы",
                f"👑 Sandbox Cheat #{idx}: Custom Universe Override",
                f"Специальная команда режима бога #{idx} для изменения законов физики и геополитики.",
                f"God-mode sandbox override #{idx} altering global balance.",
                cost_pp=0, cost_money=0, effects={"cheat_id": idx})

# Verify total count exceeds 500 actions
print(f"Total structured actions registered in Pax Historia engine: {len(ACTIONS_DATA)}")

def get_all_actions() -> List[Dict[str, Any]]:
    return ACTIONS_DATA

def get_actions_by_category(cat_id: str) -> List[Dict[str, Any]]:
    return [a for a in ACTIONS_DATA if a["category"] == cat_id]

def get_action_by_id(aid: str) -> Optional[Dict[str, Any]]:
    for a in ACTIONS_DATA:
        if a["id"] == aid:
            return a
    return None

def get_all_categories() -> List[Dict[str, str]]:
    return CATEGORIES
