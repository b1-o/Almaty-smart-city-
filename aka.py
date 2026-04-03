import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
import time
from datetime import datetime, timedelta

# Попытка импорта картографических библиотек
try:
    import folium
    from streamlit_folium import folium_static
    from folium.plugins import HeatMap, MarkerCluster
except ImportError:
    st.error("Критическая ошибка: выполните 'pip install folium streamlit-folium'")
    st.stop()

# ==============================================================================
# 1. ГЛОБАЛЬНАЯ ЛОКАЛИЗАЦИЯ (L10n) - ПОЛНЫЙ ПЕРЕВОД
# ==============================================================================
DISTRICTS = [
    "Медеуский", "Алмалинский", "Бостандыкский", "Жетысуский",
    "Ауэзовский", "Турксибский", "Наурызбайский", "Алатауский"
]

LANG_DATA = {
    "RU": {
        "title": "УМНЫЙ ГОРОД АЛМАТЫ",
        "subtitle": "Узел Интеллектуального Управления BRM",
        "nav_dashboard": "Главная панель",
        "nav_eco": "Эко-мониторинг",
        "nav_grid": "Энергосистема",
        "nav_map": "Карта событий",
        "nav_ai": "Ядро ИИ",
        "stat_traffic": "Трафик",
        "stat_aqi": "Индекс воздуха",
        "stat_temp": "Температура",
        "stat_energy": "Нагрузка сети",
        "chart_load": "История нагрузки за 24 часа",
        "chart_traffic": "Загруженность районов (баллы)",
        "chart_matrix": "Матрица здоровья города",
        "eco_alert": "ВНИМАНИЕ: Превышение уровня PM2.5 в нижних районах!",
        "grid_alert": "ПРЕДУПРЕЖДЕНИЕ: Критическая нагрузка на подстанции.",
        "ai_report_title": "Исполнительный отчет BRM",
        "ai_anomaly": "Обнаруженные аномалии",
        "ai_rec": "Рекомендация ИИ",
        "sensor_health": "Статус системы: НОМИНАЛЬНЫЙ",
        "access": "Доступ к системе",
        "refresh": "ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ",
        "footer": "Конфиденциальный доступ | Разработано BRM AI Engine 2026",
        "pm25_desc": "Частицы PM2.5 (Мелкая пыль)",
        "no2_desc": "Диоксид азота (Выхлопные газы)",
        "hum_desc": "Относительная влажность",
        "voltage_stable": "Стабильность напряжения в узлах",
        "substation_status": "Состояние узловых подстанций",
        "prediction_text": "Прогноз: Ожидается скачок потребления через 120 минут.",
        "ai_log_btn": "Скачать логи системы (.JSON)",
        "sys_online": "СИСТЕМА ОНЛАЙН ... ВСЕ ДАТЧИКИ АКТИВНЫ ... ГОРОД ПОД КОНТРОЛЕМ ..."
    },
    "KZ": {
        "title": "АЛМАТЫ АҚЫЛДЫ ҚАЛАСЫ",
        "subtitle": "BRM Интеллектуалды Басқару Түйіні",
        "nav_dashboard": "Басты панель",
        "nav_eco": "Эко-мониторинг",
        "nav_grid": "Энергия жүйесі",
        "nav_map": "Оқиғалар картасы",
        "nav_ai": "ЖИ ядросы",
        "stat_traffic": "Трафик",
        "stat_aqi": "Ауа индексі",
        "stat_temp": "Температура",
        "stat_energy": "Желі жүктемесі",
        "chart_load": "24 сағаттық жүктеме тарихы",
        "chart_traffic": "Аудандардың жүктемесі (балл)",
        "chart_matrix": "Қала денсаулығының матрицасы",
        "eco_alert": "НАЗАР АУДАРЫҢЫЗ: Төменгі аудандарда PM2.5 деңгейі жоғары!",
        "grid_alert": "ЕСКЕРТУ: Қосалқы станцияларға критикалық жүктеме.",
        "ai_report_title": "BRM Атқарушы есебі",
        "ai_anomaly": "Анықталған аномалиялар",
        "ai_rec": "ЖИ ұсынысы",
        "sensor_health": "Жүйе күйі: НОМИНАЛЬДЫ",
        "access": "Жүйеге кіру",
        "refresh": "ЖҮЙЕНІ ЖАҢАРТУ",
        "footer": "Құпия қолжетімділік | BRM AI Engine 2026 әзірлеген",
        "pm25_desc": "PM2.5 бөлшектері (Ұсақ шаң)",
        "no2_desc": "Азот диоксиді (Пайдаланылған газдар)",
        "hum_desc": "Салыстырмалы ылғалдылық",
        "voltage_stable": "Түйіндегі кернеу тұрақтылығы",
        "substation_status": "Тораптық қосалқы станциялардың күйі",
        "prediction_text": "Болжам: 120 минуттан кейін тұтынудың артуы күтілуде.",
        "ai_log_btn": "Жүйе журналдарын жүктеу (.JSON)",
        "sys_online": "ЖҮЙЕ ҚОСУЛЫ ... БАРЛЫҚ ДАТЧИКТЕР ЖҰМЫС ІСТЕП ТҰР ... ҚАЛА БАҚЫЛАУДА ..."
    },
    "EN": {
        "title": "ALMATY SMART CITY",
        "subtitle": "BRM Intelligence Control Node",
        "nav_dashboard": "Dashboard",
        "nav_eco": "Eco-Monitoring",
        "nav_grid": "Power Grid",
        "nav_map": "Event Map",
        "nav_ai": "AI Core",
        "stat_traffic": "Traffic",
        "stat_aqi": "Air Index",
        "stat_temp": "Temperature",
        "stat_energy": "Grid Load",
        "chart_load": "24h Load History",
        "chart_traffic": "District Load (Points)",
        "chart_matrix": "City Health Matrix",
        "eco_alert": "ATTENTION: PM2.5 levels exceeded in lower districts!",
        "grid_alert": "WARNING: Critical load on substations.",
        "ai_report_title": "BRM Executive Report",
        "ai_anomaly": "Anomalies Detected",
        "ai_rec": "AI Recommendation",
        "sensor_health": "System Health: NOMINAL",
        "access": "System Access",
        "refresh": "FORCE SYSTEM REFRESH",
        "footer": "Confidential Access | Powered by BRM AI Engine 2026",
        "pm25_desc": "PM2.5 Particles (Fine Dust)",
        "no2_desc": "Nitrogen Dioxide (Exhaust Fumes)",
        "hum_desc": "Relative Humidity",
        "voltage_stable": "Voltage Stability by Nodes",
        "substation_status": "Substation Operational Status",
        "prediction_text": "Forecast: Consumption spike expected in 120 minutes.",
        "ai_log_btn": "Download System Logs (.JSON)",
        "sys_online": "SYSTEM ONLINE ... ALL SENSORS FUNCTIONAL ... CITY SECURED ..."
    }
}


# ==============================================================================
# 2. ФУНКЦИЯ ТЕМАТИЗАЦИИ (ТОЛЬКО DARK MODE)
# ==============================================================================
def apply_dark_theme():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');

        /* Основной фон и текст */
        .stApp {
            background-color: #050505;
            background-image: 
                radial-gradient(at 0% 0%, rgba(0, 209, 255, 0.05) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(112, 0, 255, 0.05) 0px, transparent 50%);
            color: #e0e0e0;
            font-family: 'Inter', sans-serif;
        }

        /* Заголовок с эффектом свечения */
        .glitch-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 3.5rem;
            font-weight: 700;
            color: #ffffff;
            text-shadow: 0 0 20px rgba(0, 209, 255, 0.6);
            letter-spacing: 4px;
            margin-bottom: 0px;
        }

        /* Карточки метрик (Glassmorphism) */
        div[data-testid="stMetric"] {
            background: rgba(20, 20, 20, 0.8) !important;
            border: 1px solid rgba(0, 209, 255, 0.2) !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8) !important;
            border-radius: 15px !important;
            padding: 15px !important;
        }

        /* Стилизация табов */
        .stTabs [data-baseweb="tab-list"] {
            background-color: transparent;
            gap: 10px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 8px 8px 0 0;
            color: #888;
            padding: 10px 30px;
        }

        .stTabs [aria-selected="true"] {
            background-color: rgba(0, 209, 255, 0.2) !important;
            border-bottom: 2px solid #00d1ff !important;
            color: #00d1ff !important;
        }

        /* Кастомный контейнер AI */
        .ai-card {
            border: 1px solid #7000ff;
            background: linear-gradient(135deg, rgba(15, 15, 15, 1) 0%, rgba(30, 10, 50, 1) 100%);
            padding: 30px;
            border-radius: 20px;
            position: relative;
            overflow: hidden;
        }

        /* Анимация бегущей строки */
        marquee {
            background: #000;
            padding: 5px;
            border-top: 1px solid #222;
            border-bottom: 1px solid #222;
            font-family: 'Orbitron', sans-serif;
            font-size: 0.8rem;
        }

        /* Скрытие элементов управления темой в Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# 3. CORE ENGINE (ДВИЖОК ДАННЫХ)
# ==============================================================================
class AlmatyCore:
    @staticmethod
    @st.cache_data(ttl=60)
    def fetch_data():
        data = []
        for d in DISTRICTS:
            data.append({
                "Район": d,
                "Traffic": random.randint(2, 9),
                "AQI": random.randint(40, 280),
                "PM25": random.uniform(20, 180),
                "NO2": random.uniform(15, 90),
                "Voltage": random.uniform(218, 232),
                "Load": random.randint(50, 98),
                "Temp": random.uniform(15, 28),
                "Hum": random.randint(30, 80)
            })
        return pd.DataFrame(data).set_index("Район")

    @staticmethod
    def get_history():
        times = [datetime.now() - timedelta(minutes=30 * i) for i in range(48)]
        return pd.DataFrame({
            "Time": times,
            "Load": [random.randint(60, 95) for _ in range(48)],
            "AQI": [random.randint(50, 200) for _ in range(48)]
        }).sort_values("Time")

    @staticmethod
    def get_geo_events():
        events = []
        coords = [[43.23, 76.94], [43.25, 76.92], [43.21, 76.85], [43.32, 76.95]]
        for i in range(12):
            c = random.choice(coords)
            events.append({
                "lat": c[0] + random.uniform(-0.05, 0.05),
                "lon": c[1] + random.uniform(-0.05, 0.05),
                "type": random.choice(["Incident", "Work", "Congestion"]),
                "level": random.choice(["Low", "High", "Critical"])
            })
        return pd.DataFrame(events)


# ==============================================================================
# 4. ПОСТРОЕНИЕ ИНТЕРФЕЙСА
# ==============================================================================
st.set_page_config(page_title="BRM OS v4.0", layout="wide", initial_sidebar_state="expanded")
apply_dark_theme()

# Состояние языка
if 'lang' not in st.session_state:
    st.session_state.lang = "RU"
T = LANG_DATA[st.session_state.lang]

# Инициализация данных
engine = AlmatyCore()
df = engine.fetch_data()
hist_df = engine.get_history()
geo_df = engine.get_geo_events()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"<h2 style='font-family:Orbitron;'>🦅 BRM CORE</h2>", unsafe_allow_html=True)
    st.session_state.lang = st.radio("INTERFACE LANGUAGE", ["RU", "KZ", "EN"],
                                     index=["RU", "KZ", "EN"].index(st.session_state.lang))

    st.divider()
    st.write(f"**{T['access']}**")
    st.text_input("Token", value="••••••••", type="password")

    st.info(T["sensor_health"])
    if st.button(T["refresh"]):
        st.cache_data.clear()
        st.rerun()

# --- HEADER ---
st.markdown(f"<p class='glitch-title'>{T['title']}</p>", unsafe_allow_html=True)
st.markdown(
    f"<p style='color:#00d1ff; letter-spacing:2px;'>{T['subtitle']} | {datetime.now().strftime('%H:%M:%S')}</p>",
    unsafe_allow_html=True)

# --- TOP METRICS ---
m1, m2, m3, m4 = st.columns(4)
with m1: st.metric(T["stat_traffic"], f"{df['Traffic'].mean():.1f}/10", "-0.4")
with m2: st.metric(T["stat_aqi"], f"{int(df['AQI'].mean())} pts", "12%", delta_color="inverse")
with m3: st.metric(T["stat_temp"], f"{df['Temp'].mean():.1f}°C", "↑ 1.2")
with m4: st.metric(T["stat_energy"], f"{int(df['Load'].mean())}%", "Critical", delta_color="off")

st.divider()

# --- TABS ---
tab_1, tab_2, tab_3, tab_4, tab_5 = st.tabs([
    f"📊 {T['nav_dashboard']}", f"🌱 {T['nav_eco']}",
    f"⚡ {T['nav_grid']}", f"🗺️ {T['nav_map']}", f"🧠 {T['nav_ai']}"
])

# ТАБ 1: ДАШБОРД
with tab_1:
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader(T["chart_load"])
        fig_load = px.area(hist_df, x="Time", y="Load", color_discrete_sequence=['#00d1ff'])
        fig_load.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_load, use_container_width=True)

    with col_right:
        st.subheader(T["chart_traffic"])
        fig_bar = px.bar(df.reset_index(), x="Район", y="Traffic", color="Traffic", color_continuous_scale="Viridis")
        fig_bar.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)

# ТАБ 2: ЭКОЛОГИЯ
with tab_2:
    st.warning(T["eco_alert"])
    e1, e2 = st.columns(2)
    with e1:
        st.write(f"### {T['pm25_desc']}")
        fig_pm = px.treemap(df.reset_index(), path=["Район"], values="PM25", color="PM25",
                            color_continuous_scale="Reds")
        st.plotly_chart(fig_pm, use_container_width=True)
    with e2:
        st.write(f"### {T['no2_desc']}")
        fig_no2 = px.line_polar(df.reset_index(), r="NO2", theta="Район", line_close=True)
        fig_no2.update_traces(fill='toself', line_color='#7000ff')
        fig_no2.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_no2, use_container_width=True)

# ТАБ 3: ЭНЕРГОСЕТЬ
with tab_3:
    st.subheader(T["voltage_stable"])
    fig_v = go.Figure()
    fig_v.add_trace(
        go.Scatter(x=df.index, y=df['Voltage'], mode='lines+markers', name='VAC', line=dict(color='#00ff00')))
    fig_v.add_hline(y=220, line_dash="dash", line_color="white")
    fig_v.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_v, use_container_width=True)

    st.subheader(T["substation_status"])
    cols = st.columns(4)
    for i, district in enumerate(DISTRICTS[:4]):
        with cols[i]:
            val = df.loc[district, "Load"]
            st.write(f"**{district}**")
            st.progress(int(val))
            st.caption(f"{val}% Capacity")

# ТАБ 4: КАРТА
with tab_4:
    st.subheader("Interactive Folium Layer")
    m = folium.Map(location=[43.2389, 76.9455], zoom_start=12, tiles="CartoDB dark_matter")

    # Тепловая карта на основе AQI
    h_data = [[43.23, 76.94, 0.8], [43.25, 76.90, 0.9], [43.30, 76.95, 0.5]]
    HeatMap(h_data).add_to(m)

    # Маркеры инцидентов
    for _, row in geo_df.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=10,
            color="red" if row['level'] == "Critical" else "orange",
            fill=True,
            popup=row['type']
        ).add_to(m)

    folium_static(m, width=1200, height=600)

# ТАБ 5: ЯДРО ИИ
with tab_5:
    st.markdown(f"""
    <div class="ai-card">
        <h2 style="color:#00d1ff; font-family:Orbitron;">{T['ai_report_title']}</h2>
        <hr style="border-color:#333;">
        <p><b>{T['ai_anomaly']}:</b> 03</p>
        <ul>
            <li>Район {df['AQI'].idxmax()}: Превышение нормы загрязнения на {int(df['AQI'].max() - 100)}%.</li>
            <li>Энергоузел {df['Load'].idxmax()}: Обнаружен перегрев трансформатора.</li>
            <li>Трафик: Зафиксирована аномальная плотность на пр. Аль-Фараби.</li>
        </ul>
        <p style="background:rgba(0,209,255,0.1); padding:15px; border-left:4px solid #00d1ff;">
            <b>{T['ai_rec']}:</b> Перенаправить 15% мощностей с ТЭЦ-1 на северный узел. Активировать систему очистки воздуха в Медеуском районе.
        </p>
        <br>
        <button style="width:100%; height:40px; border-radius:10px; border:none; background:#7000ff; color:white; font-weight:bold; cursor:pointer;">
            {T['ai_log_btn']}
        </button>
    </div>
    """, unsafe_allow_html=True)

    # Визуализация графа нейросети
    st.write("#### Neural Path Activity")
    nodes = np.random.rand(15, 2)
    fig_ai = px.scatter(nodes, x=0, y=1, size_max=60, template="plotly_dark")
    fig_ai.update_traces(marker=dict(color='#00d1ff', symbol='hexagram'))
    fig_ai.update_layout(xaxis_visible=False, yaxis_visible=False)
    st.plotly_chart(fig_ai, use_container_width=True)

# --- FOOTER ---
st.divider()
st.markdown(f"<div style='text-align:center; color:#555;'>{T['footer']}</div>", unsafe_allow_html=True)
st.markdown(f"<marquee>{T['sys_online']}</marquee>", unsafe_allow_html=True)
