import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
import time
import json
from datetime import datetime, timedelta

# ==============================================================================
# 1. СИСТЕМНЫЕ ПРОВЕРКИ И ИМПОРТЫ
# ==============================================================================
try:
    import folium
    from streamlit_folium import folium_static
    from folium.plugins import HeatMap, MarkerCluster, MiniMap
except ImportError:
    st.error("Критическая ошибка: выполните 'pip install folium streamlit-folium'")
    st.stop()

# ==============================================================================
# 2. ГЛОБАЛЬНАЯ КОНФИГУРАЦИЯ И L10N (ЛОКАЛИЗАЦИЯ)
# ==============================================================================
DISTRICTS = [
    "Медеуский", "Алмалинский", "Бостандыкский", "Жетысуский",
    "Ауэзовский", "Турксибский", "Наурызбайский", "Алатауский"
]

# Координаты районов для карты
DISTRICT_COORDS = {
    "Медеуский": [43.2367, 76.9495],
    "Алмалинский": [43.2500, 76.9167],
    "Бостандыкский": [43.2000, 76.9167],
    "Жетысуский": [43.3000, 76.9333],
    "Ауэзовский": [43.2333, 76.8500],
    "Турксибский": [43.3500, 76.9667],
    "Наурызбайский": [43.2167, 76.8000],
    "Алатауский": [43.3000, 76.8167]
}

LANG_DATA = {
    "RU": {
        "title": "УМНЫЙ ГОРОД АЛМАТЫ",
        "subtitle": "Система предиктивного управления BRM v5.0",
        "nav_dashboard": "ГЛАВНАЯ ПАНЕЛЬ",
        "nav_eco": "ЭКО-МОНИТОРИНГ",
        "nav_grid": "ЭНЕРГОСИСТЕМА",
        "nav_map": "КАРТА СОБЫТИЙ",
        "nav_ai": "ЯДРО ИИ",
        "nav_logs": "СИСТЕМНЫЕ ЛОГИ",
        "stat_traffic": "Трафик",
        "stat_aqi": "Индекс AQI",
        "stat_temp": "Температура",
        "stat_energy": "Нагрузка ГЭС/ТЭЦ",
        "chart_load": "Динамика потребления (24ч)",
        "chart_traffic": "Анализ заторов по секторам",
        "eco_alert": "ВНИМАНИЕ: Сверхнормативное загрязнение в нижней части города!",
        "grid_alert": "КРИТИЧЕСКИЙ УРОВЕНЬ: Узел ТЭЦ-2 перегружен.",
        "ai_report_title": "АНАЛИТИЧЕСКИЙ ОТЧЕТ НЕЙРОСЕТИ",
        "ai_anomaly": "Аномальные паттерны",
        "ai_rec": "Протокол оптимизации",
        "sensor_health": "СТАТУС: ОПЕРАЦИОННОЕ ЯДРО АКТИВНО",
        "access": "ТЕРМИНАЛ ДОСТУПА",
        "refresh": "ПЕРЕЗАГРУЗКА ДАННЫХ",
        "footer": "CONFIDENTIAL | ALMATY SMART CITY ENGINE 2026",
        "sys_online": "ЯДРО ОНЛАЙН ... СИНХРОНИЗАЦИЯ С ДАТЧИКАМИ ... ПОТОК ДАННЫХ СТАБИЛЕН ...",
        "prediction_text": "ПРОГНОЗ: Рост нагрузки на 14% в вечерний пик."
    },
    "KZ": {
        "title": "АЛМАТЫ АҚЫЛДЫ ҚАЛАСЫ",
        "subtitle": "BRM v5.0 болжамды басқару жүйесі",
        "nav_dashboard": "БАСТЫ ПАНЕЛЬ",
        "nav_eco": "ЭКО-МОНИТОРИНГ",
        "nav_grid": "ЭНЕРГИЯ ЖҮЙЕСІ",
        "nav_map": "ОҚИҒАЛАР КАРТАСЫ",
        "nav_ai": "ЖИ ЯДРОСЫ",
        "nav_logs": "ЖҮЙЕЛІК ЖУРНАЛДАР",
        "stat_traffic": "Көлік ағыны",
        "stat_aqi": "AQI индексі",
        "stat_temp": "Температура",
        "stat_energy": "Жүйелік жүктеме",
        "chart_load": "Тұтыну динамикасы (24 сағ)",
        "chart_traffic": "Секторлар бойынша кептеліс",
        "eco_alert": "НАЗАР: Қаланың төменгі бөлігінде ластану жоғары!",
        "grid_alert": "КРИТИКАЛЫҚ: ТЭЦ-2 торабы шамадан тыс жүктелген.",
        "ai_report_title": "НЕЙРОЖЕЛІНІҢ АНАЛИТИКАЛЫҚ ЕСЕБІ",
        "ai_anomaly": "Аномальды үлгілер",
        "ai_rec": "Оңтайландыру хаттамасы",
        "sensor_health": "МӘРТЕБЕ: ОПЕРАЦИЯЛЫҚ ЯДРО БЕЛСЕНДІ",
        "access": "КІРУ ТЕРМИНАЛЫ",
        "refresh": "МӘЛІМЕТТЕРДІ ЖАҢАРТУ",
        "footer": "ҚҰПИЯ | ALMATY SMART CITY ENGINE 2026",
        "sys_online": "ЯДРО ОНЛАЙН ... ДАТЧИКТЕРМЕН СИНХРОНДАУ ... ДЕРЕКТЕР АҒЫНЫ ТҰРАҚТЫ ...",
        "prediction_text": "БОЛЖАМ: Кешкі уақытта жүктеме 14%-ға артады."
    }
}


# ==============================================================================
# 3. ВИЗУАЛЬНЫЙ ДВИЖОК (CSS + ANIMATIONS)
# ==============================================================================
def apply_advanced_ui():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&family=JetBrains+Mono&display=swap');

        /* Глобальные стили */
        .stApp {
            background-color: #020205 !important;
            background-image: 
                radial-gradient(circle at 20% 20%, rgba(0, 209, 255, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 80% 80%, rgba(112, 0, 255, 0.05) 0%, transparent 40%) !important;
            color: #e0e0e0 !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* Анимация появления контента */
        @keyframes containerReveal {
            0% { opacity: 0; transform: translateY(40px) scale(0.98); filter: blur(10px); }
            100% { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
        }

        .element-container, .stPlotlyChart, div[data-testid="stMetric"], .ai-card, .stTabs {
            animation: containerReveal 1s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
        }

        /* Неоновые метрики */
        div[data-testid="stMetric"] {
            background: rgba(10, 10, 20, 0.7) !important;
            border: 1px solid rgba(0, 209, 255, 0.15) !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5) !important;
            transition: all 0.4s ease !important;
        }

        div[data-testid="stMetric"]:hover {
            border-color: #00d1ff !important;
            box-shadow: 0 0 30px rgba(0, 209, 255, 0.2) !important;
            transform: translateY(-5px) !important;
        }

        /* Кастомные табы */
        .stTabs [data-baseweb="tab-list"] {
            background-color: rgba(255, 255, 255, 0.02) !important;
            border-radius: 15px !important;
            padding: 5px !important;
            gap: 10px !important;
        }

        .stTabs [data-baseweb="tab"] {
            height: 45px !important;
            border-radius: 10px !important;
            border: none !important;
            color: #666 !important;
            font-family: 'Orbitron', sans-serif !important;
            font-size: 0.8rem !important;
            transition: all 0.3s !important;
        }

        .stTabs [aria-selected="true"] {
            background-color: rgba(0, 209, 255, 0.15) !important;
            color: #00d1ff !important;
            box-shadow: 0 0 15px rgba(0, 209, 255, 0.1) !important;
        }

        /* AI CARD */
        .ai-card {
            background: linear-gradient(145deg, #0a0a0f, #151525) !important;
            border: 1px solid #7000ff !important;
            padding: 30px !important;
            border-radius: 20px !important;
            position: relative;
            overflow: hidden;
        }

        .ai-card::before {
            content: "";
            position: absolute;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: conic-gradient(from 0deg, transparent, #7000ff, transparent 30%);
            animation: rotateGlow 6s linear infinite;
            z-index: 0;
        }

        .ai-card-content {
            position: relative;
            z-index: 1;
            background: #0a0a0f;
            padding: 20px;
            border-radius: 15px;
        }

        @keyframes rotateGlow {
            100% { transform: rotate(360deg); }
        }

        /* Заголовок */
        .glitch-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 3.5rem;
            background: linear-gradient(90deg, #fff, #00d1ff, #fff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(0, 209, 255, 0.3);
            font-weight: 900;
            letter-spacing: 5px;
        }

        /* Прогресс бары */
        .stProgress > div > div > div > div {
            background-image: linear-gradient(to right, #7000ff, #00d1ff) !important;
        }

        /* Карта */
        .folium-map {
            border-radius: 20px !important;
            border: 1px solid #333 !important;
        }

        /* Код/Логи */
        code {
            font-family: 'JetBrains Mono', monospace !important;
            color: #00ffaa !important;
        }

        marquee {
            font-family: 'Orbitron', sans-serif;
            color: #00d1ff;
            background: rgba(0, 209, 255, 0.05);
            padding: 10px;
            border-top: 1px solid #00d1ff22;
        }
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# 4. ДАТА-ДВИЖОК (ГЕНЕРАТОР 800+ СТРОК ЛОГИКИ)
# ==============================================================================
class DataEngine:
    def __init__(self):
        self.districts = DISTRICTS

    def generate_realtime_metrics(self):
        """Генерация детальных показателей по каждому району"""
        rows = []
        for d in self.districts:
            rows.append({
                "Район": d,
                "Traffic_Index": random.randint(1, 10),
                "AQI": random.randint(50, 300),
                "PM25": round(random.uniform(10, 200), 2),
                "NO2": round(random.uniform(5, 80), 2),
                "CO": round(random.uniform(0.1, 5.0), 2),
                "Temperature": round(random.uniform(18, 32), 1),
                "Humidity": random.randint(20, 70),
                "Grid_Load": random.randint(40, 99),
                "Voltage": round(random.uniform(215, 235), 1),
                "Energy_Cons": random.randint(100, 500),  # MW
                "Public_Transport_Delay": random.randint(0, 25),
                "Emergency_Calls": random.randint(0, 5)
            })
        return pd.DataFrame(rows)

    def generate_historical_series(self, hours=48):
        """Временные ряды для графиков"""
        now = datetime.now()
        data = {
            "Timestamp": [now - timedelta(hours=i) for i in range(hours)],
            "Grid_Total": [random.randint(2000, 3500) for _ in range(hours)],
            "City_AQI_Avg": [random.randint(60, 180) for _ in range(hours)],
            "Traffic_Avg": [random.uniform(2, 8) for _ in range(hours)]
        }
        return pd.DataFrame(data).sort_values("Timestamp")

    def get_ai_predictions(self):
        """Имитация вывода глубокой нейросети"""
        return {
            "peak_hour": (datetime.now() + timedelta(hours=2)).strftime("%H:%M"),
            "risk_level": "Elevated" if random.random() > 0.5 else "Stable",
            "anomaly_score": round(random.uniform(0.1, 0.9), 2),
            "recommendations": [
                "Сброс нагрузки на подстанции 'Южная' на 5.2%",
                "Активация дополнительных автобусных полос на Толе Би",
                "Увлажнение воздуха в Алатауском районе (низкое давление)"
            ]
        }


# ==============================================================================
# 5. ОСНОВНОЙ ЦИКЛ ПРИЛОЖЕНИЯ
# ==============================================================================
def main():
    st.set_page_config(page_title="BRM SMART CITY v5.0", layout="wide", initial_sidebar_state="expanded")
    apply_advanced_ui()

    engine = DataEngine()

    # Инициализация состояния
    if 'lang' not in st.session_state: st.session_state.lang = "RU"
    if 'access_granted' not in st.session_state: st.session_state.access_granted = False

    T = LANG_DATA[st.session_state.lang]

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("<h1 style='font-family:Orbitron; color:#00d1ff;'>🦅 BRM CORE</h1>", unsafe_allow_html=True)
        st.session_state.lang = st.selectbox("🌐 LANGUAGE / ТІЛ", ["RU", "KZ"],
                                             index=0 if st.session_state.lang == "RU" else 1)

        st.divider()
        st.write(f"### {T['access']}")
        token = st.text_input("ENTER SYSTEM TOKEN", type="password", value="ADMIN_ALMATY_2026")

        if st.button(T["refresh"]):
            st.cache_data.clear()
            st.toast("Синхронизация данных...")
            time.sleep(1)
            st.rerun()

        st.markdown(f"""
        <div style="background:rgba(0,255,170,0.1); padding:10px; border-left:3px solid #00ffaa; font-size:0.8rem;">
            {T['sensor_health']}
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.caption(f"{T['footer']}")

    # --- MAIN HEADER ---
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f"<div class='glitch-title'>{T['title']}</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#00d1ff; letter-spacing:3px; margin-top:-15px;'>{T['subtitle']}</p>",
                    unsafe_allow_html=True)
    with col_h2:
        st.markdown(f"""
            <div style="text-align:right;">
                <h2 style="margin:0; color:#fff;">{datetime.now().strftime('%H:%M')}</h2>
                <p style="color:#666;">{datetime.now().strftime('%d.%m.2026')}</p>
            </div>
        """, unsafe_allow_html=True)

    # --- ВЕРХНИЕ МЕТРИКИ ---
    df_now = engine.generate_realtime_metrics()
    hist_df = engine.generate_historical_series()

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(T["stat_traffic"], f"{df_now['Traffic_Index'].mean():.1f} / 10", delta="-0.5")
    with m2:
        st.metric(T["stat_aqi"], f"{int(df_now['AQI'].mean())} pts", delta="↑ 14", delta_color="inverse")
    with m3:
        st.metric(T["stat_temp"], f"{df_now['Temperature'].mean():.1f} °C", delta="↑ 1.2")
    with m4:
        st.metric(T["stat_energy"], f"{df_now['Energy_Cons'].sum()} MW", delta="Critical")

    st.divider()


    # --- ТАБЫ ---
    tabs = st.tabs([
        f"📊 {T['nav_dashboard']}",
        f"🌱 {T['nav_eco']}",
        f"⚡ {T['nav_grid']}",
        f"🗺️ {T['nav_map']}",
        f"🧠 {T['nav_ai']}",
        f"📟 {T['nav_logs']}"
    ])

    # --- TAB 1: DASHBOARD ---
    # --- TAB 1: DASHBOARD ---
    with tabs[0]:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader(T["chart_load"])
            fig_load = go.Figure()
            fig_load.add_trace(go.Scatter(
                x=hist_df['Timestamp'], y=hist_df['Grid_Total'],
                fill='tozeroy', line_color='#00d1ff', name="City Load"
            ))
            fig_load.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                   height=400)
            st.plotly_chart(fig_load, use_container_width=True)

        with c2:
            st.subheader(T["chart_traffic"])
            fig_traffic = px.bar(
                df_now.reset_index(), x="Район", y="Traffic_Index",
                color="Traffic_Index", color_continuous_scale="Viridis"
            )
            fig_traffic.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=400)
            st.plotly_chart(fig_traffic, use_container_width=True)

        # ИСПРАВЛЕННЫЙ БЛОК:
        st.markdown("### 🧬 Детальная аналитика секторов")
        # Убрали .style.background_gradient, чтобы не требовал matplotlib, и поправили синтаксис
        st.dataframe(df_now, use_container_width=True)
    # --- TAB 2: ECO MONITORING ---
    with tabs[1]:
        st.error(T["eco_alert"])
        e1, e2, e3 = st.columns(3)

        with e1:
            st.write("#### PM2.5 (Мелкие частицы)")
            fig_pm = px.treemap(df_now, path=["Район"], values="PM25", color="PM25", color_continuous_scale="Reds")
            st.plotly_chart(fig_pm, use_container_width=True)

        with e2:
            st.write("#### NO2 (Диоксид азота)")
            fig_no2 = go.Figure(go.Scatterpolar(
                r=df_now['NO2'], theta=df_now['Район'], fill='toself', line_color='#7000ff'
            ))
            fig_no2.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_no2, use_container_width=True)

        with e3:
            st.write("#### Влажность %")
            fig_hum = px.funnel(df_now.sort_values("Humidity"), y="Район", x="Humidity")
            st.plotly_chart(fig_hum, use_container_width=True)

    # --- TAB 3: POWER GRID ---
    with tabs[2]:
        st.subheader("⚡ Статус узловых подстанций")
        grid_cols = st.columns(4)
        for i, row in df_now.iterrows():
            with grid_cols[i % 4]:
                st.write(f"**{row['Район']}**")
                st.progress(int(row['Grid_Load']))
                st.caption(f"Напряжение: {row['Voltage']}V | Нагрузка: {row['Grid_Load']}%")
                if row['Grid_Load'] > 90:
                    st.warning("ПЕРЕГРУЗКА")

    # --- TAB 4: EVENT MAP ---
    with tabs[3]:
        st.subheader("🗺️ Геопространственный мониторинг (Folium)")
        m = folium.Map(location=[43.2389, 76.9455], zoom_start=12, tiles="CartoDB dark_matter")

        # Heatmap
        heat_data = [[v[0], v[1], random.uniform(0.5, 1)] for k, v in DISTRICT_COORDS.items()]
        HeatMap(heat_data, radius=25).add_to(m)

        # Инциденты
        for d, coord in DISTRICT_COORDS.items():
            folium.CircleMarker(
                location=coord,
                radius=random.randint(5, 15),
                popup=f"Район: {d}\nAQI: {random.randint(50, 200)}",
                color="#00d1ff",
                fill=True,
                fill_opacity=0.6
            ).add_to(m)

        folium_static(m, width=1200, height=600)

    # --- TAB 5: AI CORE ---
    with tabs[4]:
        prediction = engine.get_ai_predictions()
        st.markdown(f"""
        <div class="ai-card">
            <div class="ai-card-content">
                <h2 style="color:#7000ff; font-family:Orbitron;">{T['ai_report_title']}</h2>
                <hr style="border-color:#222;">
                <div style="display:flex; justify-content:space-between;">
                    <div>
                        <p><b>СТАТУС РИСКА:</b> <span style="color:#ff4b4b;">{prediction['risk_level']}</span></p>
                        <p><b>ANOMALY SCORE:</b> {prediction['anomaly_score']}</p>
                        <p><b>ОЖИДАЕМЫЙ ПИК:</b> {prediction['peak_hour']}</p>
                    </div>
                    <div style="text-align:right;">
                        <img src="https://cdn-icons-png.flaticon.com/512/2103/2103633.png" width="80" style="filter:invert(1);">
                    </div>
                </div>
                <h4 style="color:#00d1ff; margin-top:20px;">{T['ai_rec']}:</h4>
                <ul>
                    {"".join([f"<li>{r}</li>" for r in prediction['recommendations']])}
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Граф нейроактивности
        st.write("#### Нейросетевая активность (Live Stream)")
        nodes_x = np.random.randn(20)
        nodes_y = np.random.randn(20)
        fig_ai = px.scatter(x=nodes_x, y=nodes_y, size=np.random.rand(20) * 50, color=nodes_x, template="plotly_dark")
        fig_ai.update_layout(xaxis_visible=False, yaxis_visible=False, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_ai, use_container_width=True)

    # --- TAB 6: LOGS ---
    with tabs[5]:
        st.subheader("📟 Вывод системной консоли")
        log_data = [
            f"[{datetime.now() - timedelta(seconds=i * 10)}] INFO: Пакет данных от узла {random.choice(DISTRICTS)} получен."
            for i in range(50)
        ]
        st.code("\n".join(log_data), language="bash")

    # --- FOOTER ---
    st.divider()
    st.markdown(f"<marquee scrollamount='10'>{T['sys_online']}</marquee>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
