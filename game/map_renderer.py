"""
Dynamic World Map & Frontline Renderer for Pax Historia (PNG & SVG)
Generates high-resolution graphical maps for Telegram photos and Web Live Preview.
"""
import io
import math
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont

# Province / Nation coordinates on the 2D world projection
PROVINCE_COORDS: Dict[str, Tuple_coords := Dict[str, Any]] = {
    # Russia
    "Москва": {"x": 580, "y": 200, "r": 24, "owner": "russia"},
    "Санкт-Петербург": {"x": 540, "y": 170, "r": 20, "owner": "russia"},
    "Урал": {"x": 680, "y": 210, "r": 35, "owner": "russia"},
    "Сибирь": {"x": 820, "y": 190, "r": 48, "owner": "russia"},
    "Дальний Восток": {"x": 960, "y": 230, "r": 42, "owner": "russia"},
    "Крым": {"x": 560, "y": 255, "r": 16, "owner": "russia"},
    "Донбасс": {"x": 575, "y": 245, "r": 18, "owner": "russia"},
    
    # USA
    "Вашингтон": {"x": 260, "y": 240, "r": 22, "owner": "usa"},
    "Нью-Йорк": {"x": 280, "y": 225, "r": 20, "owner": "usa"},
    "Калифорния": {"x": 160, "y": 250, "r": 28, "owner": "usa"},
    "Техас": {"x": 210, "y": 280, "r": 30, "owner": "usa"},
    "Флорида": {"x": 250, "y": 290, "r": 18, "owner": "usa"},
    "Аляска": {"x": 120, "y": 130, "r": 32, "owner": "usa"},
    "Гавайи": {"x": 90, "y": 320, "r": 14, "owner": "usa"},

    # China
    "Пекин": {"x": 840, "y": 280, "r": 24, "owner": "china"},
    "Шанхай": {"x": 880, "y": 310, "r": 20, "owner": "china"},
    "Шэньчжэнь": {"x": 860, "y": 340, "r": 18, "owner": "china"},
    "Сычуань": {"x": 800, "y": 320, "r": 28, "owner": "china"},
    "Синьцзян": {"x": 740, "y": 260, "r": 35, "owner": "china"},
    "Тибет": {"x": 760, "y": 320, "r": 30, "owner": "china"},

    # Europe
    "Брюссель": {"x": 480, "y": 210, "r": 16, "owner": "eu"},
    "Париж": {"x": 465, "y": 225, "r": 18, "owner": "eu"},
    "Берлин": {"x": 505, "y": 200, "r": 18, "owner": "eu"},
    "Рим": {"x": 500, "y": 250, "r": 16, "owner": "eu"},
    "Мадрид": {"x": 435, "y": 260, "r": 18, "owner": "eu"},
    "Варшава": {"x": 530, "y": 205, "r": 18, "owner": "eu"},

    # India
    "Нью-Дели": {"x": 720, "y": 340, "r": 22, "owner": "india"},
    "Мумбаи": {"x": 705, "y": 370, "r": 20, "owner": "india"},
    "Бангалор": {"x": 720, "y": 400, "r": 18, "owner": "india"},

    # Ukraine
    "Киев": {"x": 545, "y": 225, "r": 18, "owner": "ukraine"},
    "Харьков": {"x": 565, "y": 225, "r": 16, "owner": "ukraine"},
    "Одесса": {"x": 545, "y": 245, "r": 16, "owner": "ukraine"},
    "Львов": {"x": 525, "y": 225, "r": 16, "owner": "ukraine"},

    # Middle East
    "Тегеран": {"x": 640, "y": 290, "r": 24, "owner": "iran"},
    "Исфахан": {"x": 635, "y": 315, "r": 20, "owner": "iran"},
    "Иерусалим": {"x": 575, "y": 300, "r": 14, "owner": "israel"},
    "Тель-Авив": {"x": 570, "y": 295, "r": 12, "owner": "israel"}
}

def render_world_map_png(game_state_dict: Dict[str, Any]) -> bytes:
    """Generates a high-quality 1100x650 PNG map image."""
    width, height = 1100, 650
    img = Image.new("RGB", (width, height), color="#0F172A") # Slate dark navy ocean
    draw = ImageDraw.Draw(img)

    player_nid = game_state_dict.get("player_nation", "russia")
    nations = game_state_dict.get("nations", {})
    player = nations.get(player_nid, {})

    # Draw grid lines for tactical military map feel
    for x in range(0, width, 50):
        draw.line([(x, 60), (x, height - 70)], fill="#1E293B", width=1)
    for y in range(60, height - 70, 50):
        draw.line([(0, y), (width, y)], fill="#1E293B", width=1)

    # Color mapping
    colors = {
        "russia": "#0284C7",
        "usa": "#1D4ED8",
        "china": "#DC2626",
        "eu": "#4F46E5",
        "india": "#F97316",
        "ukraine": "#EAB308",
        "iran": "#15803D",
        "israel": "#0EA5E9"
    }

    # Draw Provinces
    for pname, pdata in PROVINCE_COORDS.items():
        owner = pdata["owner"]
        col = colors.get(owner, "#64748B")
        x, y, r = pdata["x"], pdata["y"], pdata["r"]

        # If owned by player, highlight with gold outer glow
        if owner == player_nid:
            draw.ellipse([x - r - 4, y - r - 4, x + r + 4, y + r + 4], fill="#F59E0B")
        
        draw.ellipse([x - r, y - r, x + r, y + r], fill=col, outline="#FFFFFF", width=2)
        
        # Province label
        draw.text((x - 15, y - 6), pname[:4], fill="#FFFFFF")

    # Draw Active Frontline Conflict Zones (e.g. Ukraine vs Russia, Israel vs Iran)
    # Frontline 1: Russia - Ukraine
    draw.line([(555, 215), (570, 255)], fill="#EF4444", width=5)
    draw.text((550, 230), "⚔️ 115D", fill="#F87171")

    # Frontline 2: Middle East
    draw.line([(580, 295), (630, 305)], fill="#EF4444", width=3)
    draw.text((595, 290), "💥 STRIKE", fill="#FCA5A5")

    # Draw Top HUD Banner
    draw.rectangle([0, 0, width, 60], fill="#1E293B")
    draw.line([(0, 60), (width, 60)], fill="#3B82F6", width=2)
    
    date_str = f"{game_state_dict.get('current_day', 1)}/{game_state_dict.get('current_month', 1)}/{game_state_dict.get('current_year', 2026)}"
    p_name = player.get("name_ru", "Держава")
    p_leader = player.get("leader", "Лидер")
    st = player.get("stability", 75)
    gdp = player.get("gdp_billions", 500)
    treasury = player.get("treasury_billions", 50)
    army = player.get("army_divisions", 50)
    net_status = player.get("internet_status", "ONLINE")
    gps = "JAMMED 🛰️" if player.get("gps_jamming_active") else "CLEAR 🟢"

    draw.text((20, 12), f"🌍 PAX HISTORIA 2026 | {date_str} | ХОД #{game_state_dict.get('turn_count', 0)}", fill="#38BDF8")
    draw.text((20, 34), f"👑 {p_name} ({p_leader}) | ВВП: ${gdp:,.0f}B | Казна: ${treasury:,.0f}B | Армия: {army} див.", fill="#F8FAFC")
    draw.text((700, 12), f"📶 ИНТЕРНЕТ: {net_status} | РЭБ/GPS: {gps}", fill="#FBBF24")
    draw.text((700, 34), f"🛡️ Стабильность: {st}% | Мировая напряженность: {game_state_dict.get('world_tension', 45)}%", fill="#34D399")

    # Draw Bottom Legend & Mini-Status
    draw.rectangle([0, height - 60, width, height], fill="#1E293B")
    draw.line([(0, height - 60), (width, height - 60)], fill="#475569", width=1)
    draw.text((20, height - 42), "🔵 Россия   🔴 Китай   🔷 США   🟣 ЕС   🟠 Индия   🟡 Украина   🟢 Иран   🟦 Израиль", fill="#CBD5E1")
    draw.text((780, height - 42), "⚡ Авто-скип хода: До 1 месяца | Нелинейная симуляция", fill="#94A3B8")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()

def render_world_map_svg(game_state_dict: Dict[str, Any]) -> str:
    """Generates an SVG map representation for Web Browser display."""
    width, height = 1000, 550
    player_nid = game_state_dict.get("player_nation", "russia")
    nations = game_state_dict.get("nations", {})
    player = nations.get(player_nid, {})

    svg_parts = [
        f'<svg width="100%" height="100%" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="background:#0b132b; border-radius:12px;">',
        '<!-- Grid -->',
        '<defs>',
        '<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">',
        '<path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1c2541" stroke-width="1"/>',
        '</pattern>',
        '</defs>',
        f'<rect width="{width}" height="{height}" fill="url(#grid)" />'
    ]

    colors = {
        "russia": "#0284c7",
        "usa": "#1d4ed8",
        "china": "#dc2626",
        "eu": "#4f46e5",
        "india": "#f97316",
        "ukraine": "#eab308",
        "iran": "#15803d",
        "israel": "#0ea5e9"
    }

    # Provinces
    for pname, pdata in PROVINCE_COORDS.items():
        owner = pdata["owner"]
        col = colors.get(owner, "#64748b")
        x = int(pdata["x"] * (width / 1100.0))
        y = int(pdata["y"] * (height / 650.0))
        r = pdata["r"]
        
        is_player = (owner == player_nid)
        stroke = "#f59e0b" if is_player else "#ffffff"
        swidth = 3 if is_player else 1.5

        svg_parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}" stroke="{stroke}" stroke-width="{swidth}" opacity="0.9"/>')
        svg_parts.append(f'<text x="{x}" y="{y+4}" font-family="Arial" font-size="11" fill="#ffffff" text-anchor="middle" font-weight="bold">{pname[:4]}</text>')

    # Frontlines
    svg_parts.append('<line x1="500" y1="180" x2="520" y2="215" stroke="#ef4444" stroke-width="4" stroke-dasharray="4,4"/>')
    svg_parts.append('<text x="535" y="200" fill="#f87171" font-size="12" font-weight="bold">⚔️ Фронт</text>')

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)
