// Pax Historia 2026 - Interactive Web Studio & Telegram Simulator
const USER_ID = 10001;
let currentGameState = null;
let allActions = [];
let allCategories = [];
let allPrompts = {};
let currentPromptCat = "jump_forward";

document.addEventListener("DOMContentLoaded", async () => {
    initTabs();
    await loadInitialState();
    await loadActionsCatalog();
    await loadPrompts();
    await loadScenarios();
    setupEventListeners();
});

// Tab Navigation
function initTabs() {
    const navButtons = document.querySelectorAll(".nav-item");
    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            navButtons.forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            const targetId = btn.getAttribute("data-tab");
            document.getElementById(targetId).classList.add("active");
        });
    });
}

// Initial State Loading
async function loadInitialState() {
    try {
        const resp = await fetch(`/api/state?user_id=${USER_ID}`);
        currentGameState = await resp.json();
        updateHUD();
        populateStatsEditor();
        renderInitialTelegramMessage();
        refreshLiveMap();
    } catch (e) {
        console.error("Error loading state:", e);
    }
}

function updateHUD() {
    if (!currentGameState) return;
    const p = currentGameState.nations[currentGameState.player_nation];
    document.getElementById("hud-nation").innerText = `${p.name_ru} ${p.flag_emoji}`;
    document.getElementById("hud-date").innerText = `${currentGameState.current_day}/${currentGameState.current_month}/${currentGameState.current_year}`;
    document.getElementById("hud-turn").innerText = `#${currentGameState.turn_count}`;
    
    const jammingEl = document.getElementById("hud-jamming");
    if (p.gps_jamming_active) {
        jammingEl.innerText = "АКТИВНО 🛰️";
        jammingEl.className = "val badge-on";
    } else {
        jammingEl.innerText = "ВЫКЛЮЧЕНО 🟢";
        jammingEl.className = "val";
    }

    // Update Live Events Feed
    const feed = document.getElementById("live-events-feed");
    feed.innerHTML = "";
    (currentGameState.recent_events || []).forEach(ev => {
        const item = document.createElement("div");
        item.className = "event-item";
        item.innerHTML = `<strong>${ev.title_ru || 'Событие'}</strong><br><span style="color:#94a3b8;font-size:12px;">${ev.text_ru || ''}</span>`;
        feed.appendChild(item);
    });
}

function refreshLiveMap() {
    const mapImg = document.getElementById("live-map-img");
    mapImg.src = `/api/map.png?user_id=${USER_ID}&t=${Date.now()}`;
}

function populateStatsEditor() {
    if (!currentGameState) return;
    const p = currentGameState.nations[currentGameState.player_nation];
    document.getElementById("mod-gdp").value = p.gdp_billions;
    document.getElementById("mod-treasury").value = p.treasury_billions;
    document.getElementById("mod-growth").value = p.gdp_growth;
    document.getElementById("mod-tax-corp").value = p.tax_rate_corporate;

    document.getElementById("mod-army-divs").value = p.army_divisions;
    document.getElementById("mod-drone-swarms").value = p.drone_swarms;
    document.getElementById("mod-nukes").value = p.nuclear_warheads;
    document.getElementById("mod-hypersonic").value = p.hypersonic_missiles;

    document.getElementById("mod-stability").value = p.stability;
    document.getElementById("mod-war-support").value = p.war_support;
    document.getElementById("mod-pp").value = p.political_power;
    document.getElementById("mod-corruption").value = p.corruption_index;

    // Cyber toggles
    document.querySelectorAll(".btn-cyber-toggle").forEach(btn => {
        btn.classList.toggle("active", btn.getAttribute("data-val") === p.internet_status);
    });
}

// Telegram Message Stream
function renderInitialTelegramMessage() {
    const stream = document.getElementById("tg-messages-stream");
    stream.innerHTML = "";
    const p = currentGameState.nations[currentGameState.player_nation];

    appendBotMessage(
        `🏛️ <b>ДОБРО ПОЖАЛОВАТЬ В PAX HISTORIA 2026!</b><br><br>` +
        `Вы управляете державой: <b>${p.name_ru}</b> (${p.flag_emoji})<br>` +
        `👑 <b>Лидер:</b> ${p.leader} | 📅 <b>Дата:</b> ${currentGameState.current_day}/${currentGameState.current_month}/${currentGameState.current_year}<br>` +
        `📊 <b>ВВП:</b> $${p.gdp_billions.toLocaleString()}B | <b>Казна:</b> $${p.treasury_billions.toLocaleString()}B<br>` +
        `📶 <b>РЭБ/Глушение:</b> ${p.gps_jamming_active ? 'АКТИВНО 🛰️' : 'ВЫКЛ 🟢'}<br><br>` +
        `<i>⚡ Напишите любой приказ или выберите действие ниже. Время продвинется автоматически!</i>`,
        [
            [
                { text: "⚡ Быстрый ход (+1 Месяц)", action: "quick_jump" },
                { text: "🗺️ Обновить карту", action: "refresh_map" }
            ],
            [
                { text: "🎖️ Спросить советника ИИ", action: "ask_advisor" },
                { text: "🤝 Дипломатия / Саммит", action: "open_diplomacy" }
            ],
            [
                { text: "🌐 Глушение Интернета / РЭБ", action: "toggle_jamming" },
                { text: "⚡ Каталог 500+ Действий", action: "goto_catalog" }
            ]
        ]
    );
}

function appendUserMessage(text) {
    const stream = document.getElementById("tg-messages-stream");
    const msg = document.createElement("div");
    msg.className = "tg-msg user";
    msg.innerHTML = text;
    stream.appendChild(msg);
    stream.scrollTop = stream.scrollHeight;
}

function appendBotMessage(htmlContent, inlineButtons = []) {
    const stream = document.getElementById("tg-messages-stream");
    const msg = document.createElement("div");
    msg.className = "tg-msg bot";
    msg.innerHTML = htmlContent;

    if (inlineButtons && inlineButtons.length > 0) {
        const kb = document.createElement("div");
        kb.className = "tg-inline-keyboard";
        inlineButtons.forEach(row => {
            const rowDiv = document.createElement("div");
            rowDiv.className = "tg-btn-row";
            row.forEach(b => {
                const btn = document.createElement("button");
                btn.className = "tg-inline-btn";
                btn.innerText = b.text;
                btn.addEventListener("click", () => handleInlineAction(b.action));
                rowDiv.appendChild(btn);
            });
            kb.appendChild(rowDiv);
        });
        msg.appendChild(kb);
    }

    stream.appendChild(msg);
    stream.scrollTop = stream.scrollHeight;
}

async function handleInlineAction(actionKey) {
    if (actionKey === "quick_jump") {
        await executePlayerAction("");
    } else if (actionKey === "refresh_map") {
        refreshLiveMap();
    } else if (actionKey === "ask_advisor") {
        appendUserMessage("🎖️ Запрос к стратегическому ИИ-штабу...");
        const resp = await fetch("/api/advisor", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: USER_ID, query: "Общая оценка фронтов и экономики" })
        });
        const data = await resp.json();
        appendBotMessage(data.response.replace(/\n/g, "<br>"), [
            [{ text: "⚡ Исполнить приказ", action: "quick_jump" }]
        ]);
    } else if (actionKey === "open_diplomacy") {
        appendBotMessage(
            "🤝 <b>ДИПЛОМАТИЧЕСКИЙ КОРПУС:</b><br>Выберите страну для переговоров:",
            [
                [{ text: "🇨🇳 КНР (Си Цзиньпин)", action: "dip_china" }, { text: "🇺🇸 США (Президент)", action: "dip_usa" }],
                [{ text: "🇮🇳 Индия (Моди)", action: "dip_india" }, { text: "🇪🇺 Евросоюз", action: "dip_eu" }]
            ]
        );
    } else if (actionKey.startsWith("dip_")) {
        const target = actionKey.replace("dip_", "");
        const resp = await fetch("/api/diplomacy", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: USER_ID, target_nation_id: target, message: "Предложение о сотрудничестве" })
        });
        const data = await resp.json();
        appendBotMessage(data.response.replace(/\n/g, "<br>"));
    } else if (actionKey === "toggle_jamming") {
        const p = currentGameState.nations[currentGameState.player_nation];
        const newVal = !p.gps_jamming_active;
        await fetch("/api/stat_modify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: USER_ID, stat_key: "gps_jamming_active", new_value: newVal })
        });
        await loadInitialState();
        appendBotMessage(`🛰️ <b>Глушение GPS/РЭБ переключено:</b> ${newVal ? 'ВКЛЮЧЕНО 🔴' : 'ВЫКЛЮЧЕНО 🟢'}`);
    } else if (actionKey === "goto_catalog") {
        document.querySelector('[data-tab="tab-actions-catalog"]').click();
    }
}

// Action Execution & Auto-Skip
async function executePlayerAction(actionText) {
    if (actionText) {
        appendUserMessage(actionText);
    }

    const resp = await fetch("/api/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: USER_ID, action: actionText, max_days: 30 })
    });
    const data = await resp.json();
    currentGameState = data.state;
    updateHUD();
    populateStatsEditor();
    refreshLiveMap();

    let eventsHtml = "";
    (data.events || []).forEach(ev => {
        eventsHtml += `• <b>${ev.title_ru || 'Событие'}</b><br>${ev.text_ru || ''}<br><br>`;
    });

    const p = currentGameState.nations[currentGameState.player_nation];
    appendBotMessage(
        `⚡ <b>ХОД СИМУЛЯЦИИ ЗАВЕРШЕН (Авто-скип +${data.days_advanced} дн.)</b><br>` +
        `📅 <b>Дата:</b> ${data.current_date} | <b>Ход:</b> #${data.turn_count}<br>` +
        `📊 <b>ВВП:</b> $${p.gdp_billions.toLocaleString()}B | <b>Казна:</b> $${p.treasury_billions.toLocaleString()}B<br><br>` +
        `📰 <b>СВОДКА СОБЫТИЙ:</b><br>${eventsHtml}`,
        [
            [{ text: "⚡ Следующий месяц", action: "quick_jump" }, { text: "🗺️ Обновить карту", action: "refresh_map" }],
            [{ text: "🎖️ Спросить советника", action: "ask_advisor" }]
        ]
    );
}

// 500+ Actions Catalog
async function loadActionsCatalog() {
    const resp = await fetch("/api/actions_catalog");
    const data = await resp.json();
    allActions = data.actions;
    allCategories = data.categories;

    const catSelect = document.getElementById("action-category-select");
    catSelect.innerHTML = `<option value="all">Все категории (${data.total_count} действий)</option>`;
    allCategories.forEach(cat => {
        const opt = document.createElement("option");
        opt.value = cat.id;
        opt.innerText = cat.name_ru;
        catSelect.appendChild(opt);
    });

    renderActionsGrid();
}

function renderActionsGrid() {
    const container = document.getElementById("actions-rendered-list");
    const filterCat = document.getElementById("action-category-select").value;
    const filterSearch = document.getElementById("action-search-input").value.toLowerCase();

    container.innerHTML = "";
    const filtered = allActions.filter(act => {
        const matchCat = (filterCat === "all" || act.category === filterCat);
        const matchSearch = (!filterSearch || act.title_ru.toLowerCase().includes(filterSearch) || act.desc_ru.toLowerCase().includes(filterSearch));
        return matchCat && matchSearch;
    });

    filtered.slice(0, 60).forEach(act => {
        const card = document.createElement("div");
        card.className = "action-card-item";
        card.innerHTML = `
            <div class="action-card-title">${act.title_ru}</div>
            <div class="action-card-desc">${act.desc_ru}</div>
            <button class="btn-exec-action" data-id="${act.id}">Исполнить директиву (Авто-скип) ⚡</button>
        `;
        card.querySelector(".btn-exec-action").addEventListener("click", async () => {
            document.querySelector('[data-tab="tab-tg-sim"]').click();
            await executePlayerAction(act.id);
        });
        container.appendChild(card);
    });
}

// Prompts Workshop
async function loadPrompts() {
    const resp = await fetch(`/api/prompts?user_id=${USER_ID}`);
    const data = await resp.json();
    allPrompts = data.prompts;

    const list = document.getElementById("prompts-category-list");
    list.innerHTML = "";
    data.categories.forEach(cat => {
        const btn = document.createElement("button");
        btn.className = `prompt-cat-btn ${cat === currentPromptCat ? 'active' : ''}`;
        btn.innerText = `📜 ${cat}`;
        btn.addEventListener("click", () => {
            document.querySelectorAll(".prompt-cat-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentPromptCat = cat;
            document.getElementById("current-prompt-title").innerText = `Категория: ${cat}`;
            document.getElementById("prompt-editor-textarea").value = allPrompts[cat] || "";
        });
        list.appendChild(btn);
    });

    document.getElementById("prompt-editor-textarea").value = allPrompts[currentPromptCat] || "";
}

// Scenarios Grid
async function loadScenarios() {
    const resp = await fetch("/api/presets");
    const presets = await resp.json();
    const grid = document.getElementById("scenarios-rendered-grid");
    grid.innerHTML = "";

    presets.forEach(pr => {
        const card = document.createElement("div");
        card.className = "scenario-card";
        card.innerHTML = `
            <h3>${pr.name_ru}</h3>
            <p style="color:#94a3b8; font-size:13px;">${pr.description_ru}</p>
            <span style="font-size:12px; color:#38bdf8;">Эра: ${pr.era || '2026'}</span>
            <button class="btn-launch-scenario" data-id="${pr.id}">Начать кампанию 🚀</button>
        `;
        card.querySelector(".btn-launch-scenario").addEventListener("click", async () => {
            const r = await fetch("/api/newgame", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: USER_ID, preset_id: pr.id, nation_id: "russia" })
            });
            await loadInitialState();
            document.querySelector('[data-tab="tab-tg-sim"]').click();
        });
        grid.appendChild(card);
    });
}

// Event Listeners Setup
function setupEventListeners() {
    // Send message from simulator input
    document.getElementById("tg-btn-send").addEventListener("click", () => {
        const inp = document.getElementById("tg-input-text");
        const val = inp.value.trim();
        if (val) {
            executePlayerAction(val);
            inp.value = "";
        }
    });

    document.getElementById("tg-input-text").addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            document.getElementById("tg-btn-send").click();
        }
    });

    document.getElementById("btn-global-quick-jump").addEventListener("click", () => {
        executePlayerAction("");
    });

    document.getElementById("btn-refresh-sim").addEventListener("click", () => {
        loadInitialState();
    });

    // Filters for Actions
    document.getElementById("action-category-select").addEventListener("change", renderActionsGrid);
    document.getElementById("action-search-input").addEventListener("input", renderActionsGrid);

    // Save prompt
    document.getElementById("btn-save-current-prompt").addEventListener("click", async () => {
        const txt = document.getElementById("prompt-editor-textarea").value;
        await fetch("/api/prompts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: USER_ID, category: currentPromptCat, text: txt })
        });
        allPrompts[currentPromptCat] = txt;
        alert("Промпт успешно сохранен!");
    });

    // Save BYOK
    document.getElementById("btn-save-byok-settings").addEventListener("click", async () => {
        const prov = document.getElementById("byok-provider-select").value;
        const key = document.getElementById("byok-api-key").value;
        const mod = document.getElementById("byok-model-id").value;
        const endp = document.getElementById("byok-custom-endpoint").value;
        const temp = parseFloat(document.getElementById("byok-temperature").value);

        await fetch("/api/ai_config", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: USER_ID,
                provider: prov,
                api_key: key,
                model: mod,
                endpoint: endp,
                temperature: temp
            })
        });
        alert("Настройки ИИ успешно сохранены!");
    });

    document.getElementById("byok-provider-select").addEventListener("change", (e) => {
        document.getElementById("row-custom-endpoint").style.display = (e.target.value === "custom") ? "flex" : "none";
    });

    // Save stats editor
    document.querySelectorAll(".btn-save-stat").forEach(btn => {
        btn.addEventListener("click", async () => {
            const g = btn.getAttribute("data-group");
            if (g === "eco") {
                await fetch("/api/stat_modify", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_id: USER_ID, stat_key: "gdp_billions", new_value: parseFloat(document.getElementById("mod-gdp").value) })
                });
                await fetch("/api/stat_modify", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_id: USER_ID, stat_key: "treasury_billions", new_value: parseFloat(document.getElementById("mod-treasury").value) })
                });
            } else if (g === "mil") {
                await fetch("/api/stat_modify", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_id: USER_ID, stat_key: "army_divisions", new_value: parseInt(document.getElementById("mod-army-divs").value) })
                });
                await fetch("/api/stat_modify", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_id: USER_ID, stat_key: "nuclear_warheads", new_value: parseInt(document.getElementById("mod-nukes").value) })
                });
            } else if (g === "soc") {
                await fetch("/api/stat_modify", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_id: USER_ID, stat_key: "stability", new_value: parseFloat(document.getElementById("mod-stability").value) })
                });
            }
            await loadInitialState();
            alert("Показатели государства обновлены!");
        });
    });

    // Cyber Jamming Buttons
    document.querySelectorAll(".btn-cyber-toggle").forEach(btn => {
        btn.addEventListener("click", async () => {
            const val = btn.getAttribute("data-val");
            await fetch("/api/stat_modify", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_id: USER_ID, stat_key: "internet_status", new_value: val })
            });
            await loadInitialState();
        });
    });

    document.getElementById("btn-toggle-gps-jamming").addEventListener("click", async () => {
        const p = currentGameState.nations[currentGameState.player_nation];
        await fetch("/api/stat_modify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: USER_ID, stat_key: "gps_jamming_active", new_value: !p.gps_jamming_active })
        });
        await loadInitialState();
    });

    document.getElementById("btn-toggle-dpi").addEventListener("click", async () => {
        const p = currentGameState.nations[currentGameState.player_nation];
        await fetch("/api/stat_modify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: USER_ID, stat_key: "deep_packet_inspection", new_value: !p.deep_packet_inspection })
        });
        await loadInitialState();
    });

    document.getElementById("btn-launch-ai-botnet").addEventListener("click", async () => {
        document.querySelector('[data-tab="tab-tg-sim"]').click();
        await executePlayerAction("cyber_ai_disinfo_botnet");
    });
}
