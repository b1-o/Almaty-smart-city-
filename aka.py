import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
import time
from datetime import datetime, timedelta

# Импорты для карт
try:
    import folium
    from streamlit_folium import folium_static
    from folium.plugins import HeatMap
except ImportError:
    st.error("Критические библиотеки не найдены. Выполните: pip install folium streamlit-folium")
    st.stop()

# ==============================================================================
# 1. КОНСТАНТЫ И ЛОКАЛИЗАЦИЯ (L10n)
# ==============================================================================
DISTRICTS = [
    "Медеуский", "Алмалинский", "Бостандыкский", "Жетысуский",
    "Ауэзовский", "Турксибский", "Наурызбайский", "Алатауский"
]

LANG_DATA = {
    "RU": {
        "nav_dashboard": "Главная панель",
        "nav_eco": "Эко-мониторинг",
        "nav_grid": "Энергосистема",
        "nav_map": "Карта ДТП",
        "nav_ai": "Ядро AI",
        "stat_traffic": "Загрузка дорог",
        "stat_aqi": "Индекс воздуха",
        "stat_temp": "Температура",
        "stat_energy": "Нагрузка ГЭС/ТЭЦ",
        "chart_load": "График нагрузки (24ч)",
        "sensor_status": "Статус датчиков",
        "eco_alert": "Внимание! Высокая концентрация PM2.5",
        "grid_alert": "Риск перегрузки подстанций",
    },
    "KZ": {
        "nav_dashboard": "Басты панель",
        "nav_eco": "Эко-мониторинг",
        "nav_grid": "Энергия жүйесі",
        "nav_map": "ЖКО картасы",
        "nav_ai": "AI ядросы",
        "stat_traffic": "Жол жүктемесі",
        "stat_aqi": "Ауа индексі",
        "stat_temp": "Температура",
        "stat_energy": "ГЭС/ЖЭО жүктемесі",
        "chart_load": "Жүктеме кестесі (24с)",
        "sensor_status": "Датчиктер күйі",
        "eco_alert": "Назар аударыңыз! PM2.5 жоғары концентрациясы",
        "grid_alert": "Қосалқы станциялардың шамадан тыс жүктелу қаупі",
    },
    "EN": {
        "nav_dashboard": "Dashboard",
        "nav_eco": "Eco-Monitoring",
        "nav_grid": "Power Grid",
        "nav_map": "Accident Map",
        "nav_ai": "AI Core",
        "stat_traffic": "Traffic Load",
        "stat_aqi": "Air Index",
        "stat_temp": "Temperature",
        "stat_energy": "Grid Load",
        "chart_load": "Load Chart (24h)",
        "sensor_status": "Sensor Status",
        "eco_alert": "Warning! High PM2.5 level",
        "grid_alert": "Substation Overload Risk",
    }
}


# ==============================================================================
# 2. СИСТЕМА ТЕМАТИЗАЦИИ И CSS-АНИМАЦИЙ
# ==============================================================================
def apply_ui_theme():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400&display=swap');

        :root {
            --glow-color: #00d1ff;
            --bg-dark: #0e1117;
        }

        .stApp {
            background: linear-gradient(180deg, #0e1117 0%, #050505 100%);
            color: #e0e0e0;
            font-family: 'Roboto', sans-serif;
        }

        /* Анимированный заголовок */
        .glitch-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 3rem;
            font-weight: 700;
            text-transform: uppercase;
            position: relative;
            text-shadow: 0 0 10px var(--glow-color);
            animation: pulse 3s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; transform: scale(1.01); }
            100% { opacity: 1; }
        }

        /* Glassmorphism Карточки */
        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(0, 209, 255, 0.3) !important;
            backdrop-filter: blur(10px);
            border-radius: 20px !important;
            padding: 20px !important;
            transition: 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }

        div[data-testid="stMetric"]:hover {
            border: 1px solid #00d1ff !important;
            box-shadow: 0 0 25px rgba(0, 209, 255, 0.4);
            transform: translateY(-10px);
        }

        /* Анимация прогресс-баров */
        .stProgress > div > div > div > div {
            background-image: linear-gradient(to right, #00d1ff, #7000ff);
            animation: progress-load 2s ease-in-out;
        }

        @keyframes progress-load {
            from { width: 0%; }
        }

        /* Контейнер AI отчета */
        .ai-report-container {
            border-radius: 30px;
            padding: 40px;
            background: rgba(0, 0, 0, 0.6);
            border-left: 5px solid #00d1ff;
            margin: 20px 0;
            position: relative;
            overflow: hidden;
        }

        .ai-report-container::before {
            content: "";
            position: absolute;
            top: 0; left: -100%;
            width: 100%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0,209,255,0.1), transparent);
            animation: scan 4s infinite linear;
        }

        @keyframes scan {
            0% { left: -100%; }
            100% { left: 100%; }
        }

        /* Кастомные табы */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
        }

        .stTabs [data-baseweb="tab"] {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 10px 20px;
            color: #888;
        }

        .stTabs [aria-selected="true"] {
            background: #00d1ff !important;
            color: black !important;
        }
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# 3. ДВИЖОК ДАННЫХ (CORE ENGINE)
# ==============================================================================
class AlmatyDataCore:
    @staticmethod
    def get_district_stats():
        data = []
        for d in DISTRICTS:
            data.append({
                "Район": d,
                "Трафик": random.randint(1, 10),
                "AQI": random.randint(30, 260),
                "PM2_5": random.uniform(15.0, 150.0),
                "PM10": random.uniform(20.0, 200.0),
                "NO2": random.uniform(10.0, 80.0),
                "Energy_Load": random.randint(45, 98),
                "Voltage": random.uniform(215.0, 235.0),
                "Temp": random.uniform(18.0, 26.0),
                "Humidity": random.randint(20, 85)
            })
        return pd.DataFrame(data).set_index("Район")

    @staticmethod
    def get_grid_history():
        # Генерация 24 часов нагрузки
        times = [datetime.now() - timedelta(hours=i) for i in range(24)]
        loads = [random.randint(60, 95) for _ in range(24)]
        return pd.DataFrame({"Time": times, "Load %": loads}).sort_values("Time")

    @staticmethod
    def get_accident_data():
        accidents = []
        coords = {
            "Медеуский": [43.238, 76.945], "Алмалинский": [43.250, 76.920],
            "Бостандыкский": [43.210, 76.910], "Жетысуский": [43.280, 76.930],
            "Ауэзовский": [43.230, 76.850], "Турксибский": [43.340, 76.950],
            "Наурызбайский": [43.200, 76.820], "Алатауский": [43.300, 76.820]
        }
        for d, c in coords.items():
            for _ in range(random.randint(1, 3)):
                accidents.append({
                    "lat": c[0] + random.uniform(-0.015, 0.015),
                    "lon": c[1] + random.uniform(-0.015, 0.015),
                    "type": random.choice(["ДТП", "Тех.работы", "Затор"]),
                    "impact": random.choice(["Low", "Critical"]),
                    "district": d
                })
        return pd.DataFrame(accidents)


# ==============================================================================
# 4. ИНИЦИАЛИЗАЦИЯ
# ==============================================================================
st.set_page_config(page_title="Burmolda AI OS v4.0", page_icon="🦅", layout="wide")
apply_ui_theme()
engine = AlmatyDataCore()

if 'lang' not in st.session_state: st.session_state.lang = "RU"
L = LANG_DATA[st.session_state.lang]

# Загрузка данных в кэш
df = engine.get_district_stats()
grid_df = engine.get_grid_history()
acc_df = engine.get_accident_data()

# ==============================================================================
# 5. SIDEBAR (НАВИГАЦИЯ И УПРАВЛЕНИЕ)
# ==============================================================================
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🦅 Burmolda</h1>", unsafe_allow_html=True)
    st.divider()

    st.session_state.lang = st.radio("Language / Тіл / Язык", ["RU", "KZ", "EN"], horizontal=True)

    st.subheader("System Access")
    access_code = st.text_input("Access Token", type="password", value="ADMIN_ALMATY")

    st.divider()
    st.info(f"System Health: NOMINAL\nNodes Online: {len(DISTRICTS) * 42}\nUptime: 99.98%")

    if st.button("🔄 FORCE REFRESH"):
        st.cache_data.clear()
        st.rerun()

# ==============================================================================
# 6. ГЛАВНЫЙ ИНТЕРФЕЙС
# ==============================================================================
st.markdown(f"<div class='glitch-title'>{L['title'] if 'title' in L else 'Almaty Smart OS'}</div>",
            unsafe_allow_html=True)
st.write(f"🦅 **Burmolda Intelligence Node** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# KPI TOP BAR
m1, m2, m3, m4 = st.columns(4)
with m1: st.metric(L["stat_traffic"], f"{df['Трафик'].mean():.1f}/10", delta="-0.2")
with m2: st.metric(L["stat_aqi"], f"{int(df['AQI'].mean())}", delta="14%", delta_color="inverse")
with m3: st.metric(L["stat_temp"], f"{df['Temp'].mean():.1f}°C")
with m4: st.metric(L["stat_energy"], f"{int(df['Energy_Load'].mean())}%", delta="High Load")

st.divider()

# ВЕРХНИЙ ГРАФИК (Анимация Plotly)
fig_main = go.Figure()
fig_main.add_trace(go.Scatter(x=grid_df["Time"], y=grid_df["Load %"], fill='tozeroy',
                              line=dict(color='#00d1ff', width=4), name="Grid Load"))
fig_main.update_layout(template="plotly_dark", height=300, margin=dict(l=0, r=0, t=20, b=0),
                       title=L["chart_load"])
st.plotly_chart(fig_main, use_container_width=True)

# ==============================================================================
# 7. ТЕМАТИЧЕСКИЕ ВКЛАДКИ (ПОДРОБНО)
# ==============================================================================
tab_dash, tab_eco, tab_grid, tab_map, tab_ai = st.tabs([
    f"🏙️ {L['nav_dashboard']}", f"🍀 {L['nav_eco']}",
    f"⚡ {L['nav_grid']}", f"📍 {L['nav_map']}", f"🧠 {L['nav_ai']}"
])

# --- ВКЛАДКА 1: ОБЩИЙ АНАЛИЗ ---
with tab_dash:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Traffic Heatmap by District")
        fig_bar = px.bar(df.reset_index(), x="Район", y="Трафик", color="Трафик",
                         color_continuous_scale="Viridis", template="plotly_dark")
        st.plotly_chart(fig_bar, use_container_width=True)
    with c2:
        st.subheader("District Health Matrix")
        fig_heat = px.imshow(df[["AQI", "Energy_Load", "Temp", "Humidity"]].T,
                             color_continuous_scale="RdBu_r", template="plotly_dark")
        st.plotly_chart(fig_heat, use_container_width=True)

# --- ВКЛАДКА 2: ЭКОЛОГИЯ (ГЛУБОКИЕ ДАННЫЕ) ---
with tab_eco:
    st.warning(L["eco_alert"])
    e1, e2, e3 = st.columns(3)
    with e1:
        st.write("#### Частицы PM2.5")
        st.write("Мелкая пыль, проникающая в легкие. Норма: 15-25 мкг/м³.")
        fig_pm25 = px.bar(df.reset_index(), x="Район", y="PM2_5", color="PM2_5", template="plotly_dark")
        st.plotly_chart(fig_pm25, use_container_width=True)
    with e2:
        st.write("#### Оксид Азота (NO2)")
        st.write("Продукт горения топлива. Влияет на смог.")
        fig_no2 = px.scatter(df.reset_index(), x="Трафик", y="NO2", size="AQI", color="AQI", template="plotly_dark")
        st.plotly_chart(fig_no2, use_container_width=True)
    with e3:
        st.write("#### Влажность и Комфорт")
        fig_hum = px.funnel(df.reset_index(), x="Humidity", y="Район", template="plotly_dark")
        st.plotly_chart(fig_hum, use_container_width=True)

    st.markdown("""
    > **Справка Burmolda AI:** В Алматы наблюдается температурная инверсия. Холодный грязный воздух задерживается в 'чаше' гор, что требует активации системы фильтрации в Медеуском и Алмалинском районах.
    """)

# --- ВКЛАДКА 3: ЭНЕРГОСЕТИ (ИНФРАСТРУКТУРА) ---
with tab_grid:
    st.subheader("⚡ Анализ энергоузлов")
    g1, g2 = st.columns([2, 1])
    with g1:
        # Симуляция вольтажа
        st.write("#### Стабильность напряжения (V)")
        fig_volt = px.line(df.reset_index(), x="Район", y="Voltage", markers=True, template="plotly_dark")
        fig_volt.add_hline(y=220, line_dash="dash", line_color="green", annotation_text="Standard")
        st.plotly_chart(fig_volt, use_container_width=True)
    with g2:
        st.write("#### Состояние Подстанций")
        for d in DISTRICTS:
            val = df.loc[d, "Energy_Load"]
            color = "red" if val > 90 else "green"
            st.write(f"{d}: **{val}%**")
            st.progress(int(val))

    st.info("Прогноз: Пик потребления ожидается через 2 часа. Рекомендовано включение резервного блока ТЭЦ-2.")

# --- ВКЛАДКА 4: КАРТА ДТП ---
with tab_map:
    st.subheader("📍 Live Map (Folium Engine)")

    # Центр Алматы
    m = folium.Map(location=[43.2389, 76.9455], zoom_start=11, tiles="CartoDB dark_matter")

    # Добавляем тепловую карту (Heatmap) на основе AQI
    heat_data = [[43.238, 76.945, df.loc["Медеуский", "AQI"] / 300],
                 [43.250, 76.920, df.loc["Алмалинский", "AQI"] / 300],
                 [43.210, 76.910, df.loc["Бостандыкский", "AQI"] / 300]]
    HeatMap(heat_data).add_to(m)

    # Маркеры ДТП
    for _, row in acc_df.iterrows():
        icon_color = "red" if row["impact"] == "Critical" else "orange"
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=f"Alert: {row['type']} in {row['district']}",
            icon=folium.Icon(color=icon_color, icon="bolt", prefix="fa")
        ).add_to(m)

    folium_static(m, width=1100, height=500)

# --- ВКЛАДКА 5: ЯДРО AI ---
with tab_ai:
    st.markdown(f"""
    <div class='ai-report-container'>
        <h2 style='font-family: Orbitron; color: #00d1ff;'>🦅 Burmolda Executive Report</h2>
        <p style='font-size: 1.1rem;'>
            <b>Текущий протокол:</b> Оптимизация городского пространства 2.4.1<br>
            <b>Обнаруженные аномалии:</b> 3<br><br>
            1. <b>Критический AQI:</b> Район {df['AQI'].idxmax()} показывает {df['AQI'].max()} ед. Рекомендовано ограничение движения грузового транспорта.<br>
            2. <b>Энергоузел:</b> Подстанция {df['Energy_Load'].idxmax()} работает на пределе ({df['Energy_Load'].max()}%). Риск веерного отключения в секторе B.<br>
            3. <b>Трафик:</b> Ожидаемое время нормализации движения в центре — 21:30.
        </p>
        <button style='background: #00d1ff; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;'>
            Скачать полный лог систем (.JSON)
        </button>
    </div>
    """, unsafe_allow_html=True)

    # Дополнительная визуализация нейросети
    st.write("#### Активность нейронных связей ядра")
    nodes = np.random.randn(20, 2)
    fig_ai = px.scatter(nodes, x=0, y=1, opacity=0.5, template="plotly_dark")
    fig_ai.update_traces(marker=dict(size=20, color='#00d1ff', symbol='hexagram'))
    st.plotly_chart(fig_ai, use_container_width=True)

# ==============================================================================
# 8. ФУТЕР
# ==============================================================================
st.divider()
st.markdown(
    "<div style='text-align: center; color: #555;'>© 2026 Almaty Smart City Solutions | Powered by Burmolda AI Engine | Confidential Access</div>",
    unsafe_allow_html=True)

# FOOTER С ПЛАВАЮЩЕЙ ПОЛОСОЙ
st.markdown("---")
st.markdown(
    "<marquee style='color: #00d1ff; font-family: Orbitron;'>BURMOLDA AI: SYSTEM ONLINE ... ALL SENSORS FUNCTIONAL ... ALMATY SMART CITY SECURED ...</marquee>",
    unsafe_allow_html=True)