"""
State and Data Models for Pax Historia Bot (2026 Edition)
"""
import copy
from typing import Dict, List, Any, Optional

class CountryState:
    """Represents full granular statistics and state of a nation in 2026."""
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id", "unknown")
        self.name_ru = data.get("name_ru", "Государство")
        self.name_en = data.get("name_en", "Nation")
        self.leader = data.get("leader", "Лидер")
        self.ideology = data.get("ideology", "Демократия")
        self.regime_type = data.get("regime_type", "Президентская республика")
        self.capital = data.get("capital", "Столица")
        self.flag_emoji = data.get("flag_emoji", "🏳️")
        self.color = data.get("color", "#3B82F6")

        # Politics & Governance
        self.stability = float(data.get("stability", 75.0))             # 0 - 100%
        self.war_support = float(data.get("war_support", 60.0))         # 0 - 100%
        self.political_power = float(data.get("political_power", 250.0))# 0 - 1000
        self.corruption_index = float(data.get("corruption_index", 25.0)) # 0 - 100% (lower is better)
        self.ruling_party = data.get("ruling_party", "Правящая коалиция")
        self.approval_rating = float(data.get("approval_rating", 65.0)) # 0 - 100%
        self.martial_law = bool(data.get("martial_law", False))

        # Economy & Finance
        self.gdp_billions = float(data.get("gdp_billions", 500.0))
        self.gdp_growth = float(data.get("gdp_growth", 2.8))            # annual %
        self.treasury_billions = float(data.get("treasury_billions", 50.0))
        self.debt_percent_gdp = float(data.get("debt_percent_gdp", 45.0))
        self.inflation_percent = float(data.get("inflation_percent", 3.5))
        self.tax_rate_corporate = float(data.get("tax_rate_corporate", 20.0))
        self.tax_rate_income = float(data.get("tax_rate_income", 25.0))
        self.tariff_rate = float(data.get("tariff_rate", 5.0))
        self.gold_reserves_tons = float(data.get("gold_reserves_tons", 1200.0))

        # Demographics & Society
        self.population_millions = float(data.get("population_millions", 45.0))
        self.manpower_thousands = float(data.get("manpower_thousands", 1500.0))
        self.unemployment_rate = float(data.get("unemployment_rate", 4.2))
        self.quality_of_life = float(data.get("quality_of_life", 78.0))   # 0 - 100
        self.literacy_percent = float(data.get("literacy_percent", 99.0))
        
        # Cyber, Information & Internet Jamming (2026 Core Mechanics)
        self.internet_status = data.get("internet_status", "ONLINE")       # ONLINE, PARTIAL_BLACKOUT, FULL_SHUTDOWN, JAMMED
        self.internet_freedom = float(data.get("internet_freedom", 70.0))  # 0 - 100%
        self.gps_jamming_active = bool(data.get("gps_jamming_active", False))
        self.satellite_recon_active = bool(data.get("satellite_recon_active", True))
        self.cyber_defense_level = int(data.get("cyber_defense_level", 4)) # 1 - 10
        self.cyber_offense_level = int(data.get("cyber_offense_level", 4)) # 1 - 10
        self.ai_supremacy_index = float(data.get("ai_supremacy_index", 55.0)) # 0 - 100
        self.deep_packet_inspection = bool(data.get("deep_packet_inspection", False))

        # Strategic Resources (daily / stock units)
        self.resources = data.get("resources", {
            "oil_mbd": 5.2,              # Million barrels per day
            "natural_gas_bcm": 120.0,    # Billion cubic meters / yr
            "rare_earths_ktons": 45.0,   # Thousand metric tons
            "uranium_tons": 800.0,       # Metric tons
            "steel_mtons": 35.0,         # Million metric tons
            "semiconductors_index": 70,  # Supply index (0-100)
            "grain_mtons": 40.0,         # Food grain metric tons
            "energy_grid_gw": 180.0      # Gigawatts capacity
        })

        # Military & Armed Forces
        self.army_divisions = int(data.get("army_divisions", 50))
        self.armored_brigades = int(data.get("armored_brigades", 25))
        self.drone_swarms = int(data.get("drone_swarms", 40))
        self.navy_ships = int(data.get("navy_ships", 80))
        self.aircraft_carriers = int(data.get("aircraft_carriers", 2))
        self.submarines = int(data.get("submarines", 15))
        self.air_wings = int(data.get("air_wings", 45))
        self.stealth_jets = int(data.get("stealth_jets", 60))
        self.hypersonic_missiles = int(data.get("hypersonic_missiles", 30))
        self.air_defense_batteries = int(data.get("air_defense_batteries", 40))
        self.nuclear_warheads = int(data.get("nuclear_warheads", 0))
        self.military_doctrine = data.get("military_doctrine", "Сетецентрическая война (Network-Centric)")

        # Science & Technology
        self.research_points = float(data.get("research_points", 150.0))
        self.tech_era = data.get("tech_era", "Digital & AI Era 2026")
        self.unlocked_techs = data.get("unlocked_techs", [
            "drone_tactics", "5g_network", "quantum_cryptography_basics", "hypersonic_glide", "advanced_anti_air"
        ])
        self.current_research = data.get("current_research", "autonomous_ai_battlefield")

        # Territories & Provinces
        self.provinces = list(data.get("provinces", []))
        self.controlled_straits = list(data.get("controlled_straits", []))

        # Foreign Relations & Diplomacy
        self.allies = list(data.get("allies", []))
        self.non_aggression = list(data.get("non_aggression", []))
        self.at_war = list(data.get("at_war", []))
        self.puppets = list(data.get("puppets", []))
        self.guarantees = list(data.get("guarantees", []))
        self.embargoes = list(data.get("embargoes", []))
        self.relations = dict(data.get("relations", {})) # { "target_nation_id": int_score (-100 to 100) }

        # Espionage & Covert Networks
        self.spy_networks = dict(data.get("spy_networks", {})) # { "target_nation_id": int_level (0-100) }
        self.covert_ops_active = list(data.get("covert_ops_active", []))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name_ru": self.name_ru,
            "name_en": self.name_en,
            "leader": self.leader,
            "ideology": self.ideology,
            "regime_type": self.regime_type,
            "capital": self.capital,
            "flag_emoji": self.flag_emoji,
            "color": self.color,
            "stability": self.stability,
            "war_support": self.war_support,
            "political_power": self.political_power,
            "corruption_index": self.corruption_index,
            "ruling_party": self.ruling_party,
            "approval_rating": self.approval_rating,
            "martial_law": self.martial_law,
            "gdp_billions": self.gdp_billions,
            "gdp_growth": self.gdp_growth,
            "treasury_billions": self.treasury_billions,
            "debt_percent_gdp": self.debt_percent_gdp,
            "inflation_percent": self.inflation_percent,
            "tax_rate_corporate": self.tax_rate_corporate,
            "tax_rate_income": self.tax_rate_income,
            "tariff_rate": self.tariff_rate,
            "gold_reserves_tons": self.gold_reserves_tons,
            "population_millions": self.population_millions,
            "manpower_thousands": self.manpower_thousands,
            "unemployment_rate": self.unemployment_rate,
            "quality_of_life": self.quality_of_life,
            "literacy_percent": self.literacy_percent,
            "internet_status": self.internet_status,
            "internet_freedom": self.internet_freedom,
            "gps_jamming_active": self.gps_jamming_active,
            "satellite_recon_active": self.satellite_recon_active,
            "cyber_defense_level": self.cyber_defense_level,
            "cyber_offense_level": self.cyber_offense_level,
            "ai_supremacy_index": self.ai_supremacy_index,
            "deep_packet_inspection": self.deep_packet_inspection,
            "resources": self.resources,
            "army_divisions": self.army_divisions,
            "armored_brigades": self.armored_brigades,
            "drone_swarms": self.drone_swarms,
            "navy_ships": self.navy_ships,
            "aircraft_carriers": self.aircraft_carriers,
            "submarines": self.submarines,
            "air_wings": self.air_wings,
            "stealth_jets": self.stealth_jets,
            "hypersonic_missiles": self.hypersonic_missiles,
            "air_defense_batteries": self.air_defense_batteries,
            "nuclear_warheads": self.nuclear_warheads,
            "military_doctrine": self.military_doctrine,
            "research_points": self.research_points,
            "tech_era": self.tech_era,
            "unlocked_techs": self.unlocked_techs,
            "current_research": self.current_research,
            "provinces": self.provinces,
            "controlled_straits": self.controlled_straits,
            "allies": self.allies,
            "non_aggression": self.non_aggression,
            "at_war": self.at_war,
            "puppets": self.puppets,
            "guarantees": self.guarantees,
            "embargoes": self.embargoes,
            "relations": self.relations,
            "spy_networks": self.spy_networks,
            "covert_ops_active": self.covert_ops_active
        }

class GameSession:
    """Manages full game state including all nations, world news, battles, and queued actions."""
    def __init__(self, data: Dict[str, Any]):
        self.game_id = data.get("game_id", "game_1")
        self.user_id = data.get("user_id", 0)
        self.title = data.get("title", "Pax Historia 2026")
        self.preset_id = data.get("preset_id", "modern_2026")
        self.current_year = int(data.get("current_year", 2026))
        self.current_month = int(data.get("current_month", 1))
        self.current_day = int(data.get("current_day", 1))
        self.player_nation_id = data.get("player_nation", "russia")
        self.difficulty = data.get("difficulty", "normal")
        self.turn_count = int(data.get("turn_count", 0))

        # Nations Map
        nations_raw = data.get("nations", {})
        self.nations: Dict[str, CountryState] = {}
        for nid, ndata in nations_raw.items():
            self.nations[nid] = CountryState(ndata)

        # Queued player actions for current turn
        self.queued_actions: List[Dict[str, Any]] = list(data.get("queued_actions", []))

        # Recent events log & Timeline
        self.recent_events: List[Dict[str, Any]] = list(data.get("recent_events", []))
        self.timeline_log: List[Dict[str, Any]] = list(data.get("timeline_log", []))

        # Advisor Memory & Chat History
        self.advisor_history: List[Dict[str, str]] = list(data.get("advisor_history", []))
        
        # Diplomacy Bilateral Chat Histories { "nation_id": [ {role, content} ] }
        self.diplomacy_chats: Dict[str, List[Dict[str, str]]] = dict(data.get("diplomacy_chats", {}))

        # Active Wars Frontlines & Battle Progress
        self.frontlines: List[Dict[str, Any]] = list(data.get("frontlines", []))

        # Global World Modifiers
        self.world_tension = float(data.get("world_tension", 45.0)) # 0 - 100%
        self.oil_barrel_price_usd = float(data.get("oil_barrel_price_usd", 82.5))
        self.global_trade_growth = float(data.get("global_trade_growth", 2.1))

    @property
    def player_nation(self) -> Optional[CountryState]:
        return self.nations.get(self.player_nation_id)

    def get_date_str(self, lang: str = "ru") -> str:
        months_ru = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня", "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"]
        months_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        m_idx = max(0, min(11, self.current_month - 1))
        if lang == "ru":
            return f"{self.current_day} {months_ru[m_idx]} {self.current_year} г."
        return f"{months_en[m_idx]} {self.current_day}, {self.current_year}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "game_id": self.game_id,
            "user_id": self.user_id,
            "title": self.title,
            "preset_id": self.preset_id,
            "current_year": self.current_year,
            "current_month": self.current_month,
            "current_day": self.current_day,
            "player_nation": self.player_nation_id,
            "difficulty": self.difficulty,
            "turn_count": self.turn_count,
            "world_tension": self.world_tension,
            "oil_barrel_price_usd": self.oil_barrel_price_usd,
            "global_trade_growth": self.global_trade_growth,
            "nations": {nid: n.to_dict() for nid, n in self.nations.items()},
            "queued_actions": self.queued_actions,
            "recent_events": self.recent_events,
            "timeline_log": self.timeline_log,
            "advisor_history": self.advisor_history,
            "diplomacy_chats": self.diplomacy_chats,
            "frontlines": self.frontlines
        }
