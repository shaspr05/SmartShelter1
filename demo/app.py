import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Import modular components
from models.thermal_model import ThermalModel
from models.comfort_model import ComfortModel
from models.optimization_model import OptimizationModel
from engine.recommendation_engine import RecommendationEngine
from sensors.sensor_interface import ManualSensorProvider, MockIoTSensorProvider
from engine.ml_module import SmartShelterML
import utils.helpers as helpers

# Import comfort zone definitions & constants
from models.comfort_zone import (
    COLOR_THEME, 
    ZONE_DEFINITIONS, 
    get_comfort_zone, 
    get_zone_description, 
    get_thermal_condition, 
    get_zone_recommendations
)

# Set Page Config
st.set_page_config(
    page_title="SmartShelter - DRDO Hackathon Software",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling (Technical Dark Theme UI)
st.markdown("""
    <style>
    /* Dark glassmorphism panels and details */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .metric-card {
        background: rgba(22, 27, 34, 0.8);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .metric-title {
        font-size: 0.9rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        margin: 10px 0;
        color: #58a6ff;
    }
    .status-badge {
        font-size: 1.1rem;
        font-weight: bold;
        padding: 5px 12px;
        border-radius: 20px;
        display: inline-block;
    }
    
    /* Dynamic active status borders/colors */
    .status-comfortable { background-color: rgba(46, 160, 67, 0.15); color: #3fb950; border: 1px solid #2ea043; }
    .status-moderate { background-color: rgba(210, 153, 34, 0.15); color: #d29922; border: 1px solid #d29922; }
    .status-uncomfortable { background-color: rgba(240, 136, 62, 0.15); color: #f0883e; border: 1px solid #f0883e; }
    .status-critical { background-color: rgba(248, 81, 73, 0.15); color: #f85149; border: 1px solid #f85149; }
    
    .formula-box {
        background-color: #161b22;
        border-left: 5px solid #2188ff;
        padding: 15px;
        border-radius: 0 8px 8px 0;
        font-family: monospace;
        margin: 15px 0;
    }
    
    /* Headers & Text colors */
    h1, h2, h3 {
        color: #58a6ff !important;
    }
    .sidebar .sidebar-content {
        background-color: #161b22;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Core Services
@st.cache_resource
def get_services():
    thermal = ThermalModel(coeff_path="data/shelter_coefficients.json")
    comfort = ComfortModel()
    optimizer = OptimizationModel(thermal, comfort)
    engine = RecommendationEngine()
    ml = SmartShelterML()
    return thermal, comfort, optimizer, engine, ml

thermal_model, comfort_model, opt_model, rec_engine, ml_module = get_services()

# --- SCENARIOS SETUP ---
SCENARIOS = {
    "Scenario 1: Hot Desert (Thar Desert)": {
        "t_outdoor": 40.0, "humidity": 70.0, "wind_speed": 4.5, "solar_exposure": "Extreme",
        "roof": "Metal", "wall": "Metal", "ventilation": "Poor", "shading": "None", "size": "Medium (6-8 Pax)"
    },
    "Scenario 2: Hot Humid (Coastal Outpost)": {
        "t_outdoor": 36.0, "humidity": 80.0, "wind_speed": 2.5, "solar_exposure": "High",
        "roof": "Concrete", "wall": "Concrete", "ventilation": "Moderate", "shading": "Low", "size": "Medium (6-8 Pax)"
    },
    "Scenario 3: Cold Environment (Siachen/Himalayas)": {
        "t_outdoor": -10.0, "humidity": 45.0, "wind_speed": 8.0, "solar_exposure": "Low",
        "roof": "Fabric", "wall": "Fabric", "ventilation": "Poor", "shading": "None", "size": "Medium (6-8 Pax)"
    },
    "Scenario 4: Moderate Environment (Valley Command)": {
        "t_outdoor": 24.0, "humidity": 50.0, "wind_speed": 3.0, "solar_exposure": "Medium",
        "roof": "Insulated Panel", "wall": "Insulated Panel", "ventilation": "Good", "shading": "Medium", "size": "Medium (6-8 Pax)"
    },
    "Scenario 5: User Custom Scenario": {
        "t_outdoor": 30.0, "humidity": 50.0, "wind_speed": 3.0, "solar_exposure": "Medium",
        "roof": "Composite", "wall": "Composite", "ventilation": "Good", "shading": "Medium", "size": "Medium (6-8 Pax)"
    }
}

# Sidebar - Settings & Preset Scenarios
st.sidebar.image("https://img.icons8.com/color/96/shield.png", width=70)
st.sidebar.title("SMARTSHELTER")
st.sidebar.markdown("**DRDO Hackathon Prototype v2.0**")
st.sidebar.markdown("---")

st.sidebar.subheader("Select Scenario Preset")
preset_name = st.sidebar.selectbox("Load Environment Preset", list(SCENARIOS.keys()))
preset = SCENARIOS[preset_name]

st.sidebar.subheader("Environmental Inputs")
telemetry_mode = st.sidebar.toggle("Enable IoT Telemetry (Mock Feed)", value=False)

if telemetry_mode:
    iot_base_temp = st.sidebar.slider("IoT Base Temperature (°C)", 10.0, 50.0, float(preset["t_outdoor"]))
    iot_base_hum = st.sidebar.slider("IoT Base Humidity (%)", 10.0, 100.0, float(preset["humidity"]))
    iot_provider = MockIoTSensorProvider(base_temp=iot_base_temp, base_humidity=iot_base_hum)
    sensor_data = iot_provider.read_data()
    
    t_outdoor = sensor_data["outdoor_temperature"]
    humidity = sensor_data["humidity"]
    wind_speed = sensor_data["wind_speed"]
    solar_exposure = sensor_data["solar_exposure"]
    st.sidebar.info(f"Connected: {sensor_data['provider']}")
else:
    t_outdoor = st.sidebar.slider("Outdoor Temperature (°C)", -25.0, 55.0, float(preset["t_outdoor"]), step=0.5)
    humidity = st.sidebar.slider("Relative Humidity (%)", 5.0, 100.0, float(preset["humidity"]), step=1.0)
    wind_speed = st.sidebar.slider("Wind Speed (m/s)", 0.0, 20.0, float(preset["wind_speed"]), step=0.1)
    solar_exposure = st.sidebar.selectbox("Solar Exposure", ["Low", "Medium", "High", "Extreme"], 
                                          index=["Low", "Medium", "High", "Extreme"].index(preset["solar_exposure"]))

st.sidebar.subheader("Shelter Configuration Inputs")
roof_options = list(thermal_model.coefficients.get("roof", {}).keys())
wall_options = list(thermal_model.coefficients.get("wall", {}).keys())
vent_options = list(thermal_model.coefficients.get("ventilation", {}).keys())
shade_options = list(thermal_model.coefficients.get("shading", {}).keys())
size_options = list(thermal_model.coefficients.get("size", {}).keys())

roof = st.sidebar.selectbox("Roof Material", roof_options, index=roof_options.index(preset["roof"]))
wall = st.sidebar.selectbox("Wall Material", wall_options, index=wall_options.index(preset["wall"]))
ventilation = st.sidebar.selectbox("Ventilation Scheme", vent_options, index=vent_options.index(preset["ventilation"]))
shading = st.sidebar.selectbox("Shading Profile", shade_options, index=shade_options.index(preset["shading"]))
shelter_size = st.sidebar.selectbox("Shelter Size", size_options, index=size_options.index(preset.get("size", "Medium (6-8 Pax)")))

# Main Header Design
st.markdown("# 🛡️ SMARTSHELTER")
st.markdown("### Thermal Comfort & Shelter Design Optimization Suite")
st.markdown("Decision-support system for high-altitude/desert outpost shelter design optimization.")
st.markdown("---")

# Compute Core Formula & Comfort
t_indoor, breakdown = thermal_model.calculate_indoor_temperature(
    t_outdoor=t_outdoor,
    roof_material=roof,
    wall_material=wall,
    ventilation_level=ventilation,
    shading_level=shading,
    shelter_size=shelter_size
)

temp_score, humidity_penalty, final_comfort_score, comfort_status = comfort_model.calculate_comfort(
    t_indoor=t_indoor,
    humidity=humidity
)

# Resolve primary condition & zone descriptions
primary_cond = get_thermal_condition(t_indoor)
zone_desc = get_zone_description(comfort_status)
theme = COLOR_THEME[comfort_status]

# Horizontal step rendering function
def render_horizontal_steps(active_zone: str):
    zones = ["CRITICAL", "UNCOMFORTABLE", "MODERATE", "COMFORTABLE"]
    cols = st.columns(4)
    for idx, z in enumerate(zones):
        z_theme = COLOR_THEME[z]
        is_active = (z == active_zone)
        border = z_theme["border"] if is_active else "#30363d"
        bg = z_theme["bg"] if is_active else "rgba(22, 27, 34, 0.2)"
        text_color = z_theme["hex"] if is_active else "#8b949e"
        weight = "bold" if is_active else "normal"
        glow = f"box-shadow: 0 0 12px {z_theme['hex']}40;" if is_active else ""
        
        cols[idx].markdown(f"""
        <div style="border: 2px solid {border}; background-color: {bg}; border-radius: 8px; padding: 12px; text-align: center; {glow}">
            <div style="font-size: 1.4rem;">{z_theme['icon']}</div>
            <div style="font-weight: {weight}; color: {text_color}; font-size: 0.95rem; letter-spacing: 0.5px;">{z}</div>
            <div style="font-size: 0.75rem; color: #8b949e;">{ZONE_DEFINITIONS[z]['range'][0]}% – {ZONE_DEFINITIONS[z]['range'][1]}%</div>
        </div>
        """, unsafe_allow_html=True)

# Tabs
tab_dashboard, tab_optimize, tab_ml, tab_assumptions = st.tabs([
    "📊 Core Dashboard", 
    "⚡ Design Optimizer", 
    "🧠 Adaptive AI Engine", 
    "📋 Assumptions & Docs"
])

with tab_dashboard:
    # 1. Thermal Condition Card Row (Prominent values)
    st.markdown("### 🌡️ Thermal Condition Parameters")
    cond_col1, cond_col2, cond_col3 = st.columns(3)
    
    with cond_col1:
        st.markdown(f"""
            <div class="metric-card" style="border-top: 4px solid #58a6ff;">
                <div class="metric-title">OUTDOOR TEMPERATURE</div>
                <div class="metric-value">{t_outdoor:.1f}°C</div>
                <div style="font-size: 0.8rem; color: #8b949e;">Sensor/Form Reading</div>
            </div>
        """, unsafe_allow_html=True)
        
    with cond_col2:
        st.markdown(f"""
            <div class="metric-card" style="border-top: 4px solid #ff7b72;">
                <div class="metric-title">ESTIMATED INDOOR TEMPERATURE</div>
                <div class="metric-value" style="color: #ff7b72;">{t_indoor:.1f}°C</div>
                <div style="font-size: 0.8rem; color: #8b949e;">Physical Coefficient Summation</div>
            </div>
        """, unsafe_allow_html=True)
        
    with cond_col3:
        st.markdown(f"""
            <div class="metric-card" style="border-top: 4px solid {theme['hex']};">
                <div class="metric-title">THERMAL COMFORT INDEX</div>
                <div class="metric-value" style="color: {theme['hex']};">{final_comfort_score:.1f}%</div>
                <div style="font-size: 0.8rem; color: #8b949e;">Humidity-Penalized Value</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 2. Main Comfort Status Section
    st.subheader("Comfort Hazard & Zone Assessment")
    
    # 4-Level Gauge & Horizontal Indicators
    gauge_col, ind_col = st.columns([1, 1.2])
    
    with gauge_col:
        # Plotly Comfort Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = final_comfort_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"{theme['icon']} {comfort_status}", 'font': {'size': 20, 'color': theme['hex']}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#c9d1d9"},
                'bar': {'color': theme['hex']},
                'bgcolor': "rgba(22, 27, 34, 0.5)",
                'borderwidth': 2,
                'bordercolor': "#30363d",
                'steps': [
                    {'range': [0, 39], 'color': 'rgba(248, 81, 73, 0.15)'},
                    {'range': [39, 59], 'color': 'rgba(240, 136, 62, 0.15)'},
                    {'range': [59, 79], 'color': 'rgba(210, 153, 34, 0.15)'},
                    {'range': [79, 100], 'color': 'rgba(46, 160, 67, 0.15)'}
                ],
                'threshold': {
                    'line': {'color': theme['hex'], 'width': 4},
                    'thickness': 0.75,
                    'value': final_comfort_score
                }
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#c9d1d9',
            height=280,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with ind_col:
        st.markdown(f"**Zone Status Description:**")
        st.markdown(f"""
        <div style="background-color: {theme['bg']}; border: 1px solid {theme['border']}; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <h4 style="margin: 0; color: {theme['hex']};">{theme['icon']} {comfort_status} ZONE</h4>
            <p style="margin: 8px 0 0 0; font-size: 1.05rem;">{zone_desc}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Comfort Zone Progression Map:**")
        render_horizontal_steps(comfort_status)
        st.markdown(f"**Primary Thermal State:** `{primary_cond.replace('_', ' ')}`")

    st.markdown("---")

    # 3. Calculation Details & Contribution Chart
    calc_col, chart_col = st.columns([1, 1.2])
    
    with calc_col:
        st.subheader("Explain Result Calculator")
        st.markdown("Mathematical step progression used to derive estimated parameters:")
        
        st.markdown(f"""
        *   Outdoor Temperature Base: `{t_outdoor:.1f}°C`
        *   Roof Contribution ({roof}): `+{breakdown['roof']:.1f}°C`
        *   Wall Contribution ({wall}): `+{breakdown['wall']:.1f}°C`
        *   Ventilation Contribution ({ventilation}): `{breakdown['ventilation']:.1f}°C`
        *   Shading Contribution ({shading}): `{breakdown['shading']:.1f}°C`
        *   Size Contribution ({shelter_size}): `{breakdown['size']:.1f}°C`
        *   **Summation calculation:**
            `{t_outdoor:.1f} + ({breakdown['roof']}) + ({breakdown['wall']}) + ({breakdown['ventilation']}) + ({breakdown['shading']}) + ({breakdown['size']})` = **`{t_indoor:.1f}°C`**
        *   **Thermal score calculations:**
            *   Base comfort: `{temp_score:.1f}%`
            *   Humidity adjustment penalty: `{humidity_penalty:.1f}%`
            *   Final comfort percentage: **`{final_comfort_score:.1f}%`**
        """)
        
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("💾 Save Simulation Run", use_container_width=True):
                helpers.log_simulation(
                    t_outdoor, humidity, wind_speed, solar_exposure,
                    roof, wall, ventilation, shading, shelter_size, t_indoor, final_comfort_score, comfort_status, primary_cond
                )
                st.success("Simulation details successfully logged.")
        with btn_c2:
            if st.button("🔄 Reset Configuration", use_container_width=True):
                st.rerun()
                
        # Expandable help docs
        with st.expander("ℹ️ Understand Comfort Zones"):
            st.markdown("""
            | Zone | Comfort | Interpretation | Action |
            | :--- | :--- | :--- | :--- |
            | Comfortable | 80–100% | Good thermal condition | Maintain |
            | Moderate | 60–79% | Early discomfort | Improve |
            | Uncomfortable | 40–59% | Significant discomfort | Modify |
            | Critical | 0–39% | Severe modeled discomfort | Priority intervention |
            
            *Prototype comfort model. Thresholds require calibration using validated thermal-comfort standards and field measurements for real-world deployment.*
            """)

    with chart_col:
        st.subheader("Thermal Contribution Graph")
        contrib_labels = ["Outdoor Base", "Roof", "Wall", "Ventilation", "Shading", "Size"]
        contrib_vals = [t_outdoor, breakdown['roof'], breakdown['wall'], breakdown['ventilation'], breakdown['shading'], breakdown['size']]
        
        fig = go.Figure()
        colors = ['#58a6ff' if val >= 0 else '#ff7b72' for val in contrib_vals]
        colors[0] = '#2188ff'
        
        fig.add_trace(go.Bar(
            y=contrib_labels,
            x=contrib_vals,
            orientation='h',
            marker=dict(color=colors),
            text=[f"{v:+.1f}°C" if idx > 0 else f"{v:.1f}°C" for idx, v in enumerate(contrib_vals)],
            textposition='auto',
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#c9d1d9',
            xaxis_title="Impact (°C)",
            yaxis=dict(autorange="reversed"),
            margin=dict(l=20, r=20, t=10, b=10),
            height=280
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 4. Smart Recommendations Based on Zone & Contributions
    rec_col1, rec_col2 = st.columns([1.2, 1])
    
    with rec_col1:
        st.subheader("Diagnostics & Prioritized Recommendations")
        diagnostics = rec_engine.analyze_and_recommend(
            t_outdoor, humidity, wind_speed, solar_exposure,
            roof, wall, ventilation, shading, t_indoor, breakdown, comfort_status
        )
        
        for item in diagnostics:
            color_map = {"HIGH": "#f85149", "MEDIUM": "#d29922", "LOW": "#58a6ff"}
            border_color = color_map.get(item["priority"], "#30363d")
            
            st.markdown(f"""
            <div style="border: 1px solid {border_color}; border-left: 6px solid {border_color}; padding: 12px; margin-bottom: 12px; border-radius: 6px; background-color: rgba(22, 27, 34, 0.5);">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-weight: bold; color: {border_color};">{item['priority']} PRIORITY</span>
                    <span style="font-size: 0.8rem; color: #8b949e;">{comfort_status} Zone Action</span>
                </div>
                <div style="font-size: 1.05rem; font-weight: bold; margin: 4px 0;">{item['problem']}</div>
                <div style="font-size: 0.9rem; color: #8b949e; margin-bottom: 6px;"><b>Evidence:</b> {item['evidence']}</div>
                <div style="font-size: 0.95rem;"><b>Recommended Action:</b> {item['action']}</div>
            </div>
            """, unsafe_allow_html=True)

    with rec_col2:
        st.subheader("Comfort Scoring Curve Reference")
        x_range = np.linspace(-10.0, 50.0, 200)
        y_range = []
        for x in x_range:
            t_score, _, final_score, _ = comfort_model.calculate_comfort(x, humidity)
            y_range.append(final_score)
            
        fig_curve = go.Figure()
        fig_curve.add_trace(go.Scatter(
            x=x_range, y=y_range,
            mode='lines',
            line=dict(color='#58a6ff', width=3),
            name='Comfort Score'
        ))
        
        fig_curve.add_trace(go.Scatter(
            x=[t_indoor], y=[final_comfort_score],
            mode='markers+text',
            marker=dict(color=theme['hex'], size=12, symbol='circle'),
            text=[f"Current ({t_indoor:.1f}°C)"],
            textposition="top center",
            name='Shelter State'
        ))
        
        fig_curve.add_vrect(
            x0=22.0, x1=26.0,
            fillcolor="#2ea043", opacity=0.15,
            layer="below", line_width=0,
            annotation_text="Comfort Target Range",
            annotation_position="top left"
        )
        
        fig_curve.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#c9d1d9',
            xaxis_title="Indoor Temperature (°C)",
            yaxis_title="Comfort Index (%)",
            yaxis=dict(range=[-5, 105]),
            margin=dict(l=20, r=20, t=10, b=10),
            height=280
        )
        st.plotly_chart(fig_curve, use_container_width=True)

    st.markdown("---")
    
    # 5. Simulation Logs History Table with Time Series Chart
    st.subheader("📜 Simulation History & Comfort Progression")
    log_df = helpers.load_simulations()
    
    if not log_df.empty:
        col_hist1, col_hist2 = st.columns([1.2, 1])
        with col_hist1:
            st.dataframe(log_df.tail(10), use_container_width=True)
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                csv_data = log_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Export CSV Registry", csv_data, "smartshelter_simulations.csv", "text/csv", use_container_width=True)
            with col_c2:
                if st.button("🗑️ Clear Log History", use_container_width=True):
                    helpers.clear_simulations()
                    st.success("Simulation log history cleared.")
                    st.rerun()
        with col_hist2:
            # Render comfort index history chart
            fig_hist = px.line(
                log_df, 
                x=log_df.index, 
                y="Comfort Score (%)", 
                text="Status",
                title="Comfort Score Progression over Run Cycles",
                markers=True
            )
            fig_hist.update_traces(line_color="#58a6ff", marker=dict(size=8))
            fig_hist.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#c9d1d9',
                xaxis_title="Run Number",
                height=250,
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No recorded simulations found. Click 'Save Simulation Run' to log the current values.")

# Render Design Optimizer Tab
with tab_optimize:
    st.subheader("💡 Shelter Design Optimization & Permutation Comparison")
    st.markdown("""
    Evaluate all permutation configurations (combinations of Roof, Wall, Shading, and Ventilation) under the current environmental conditions to find the design with the highest Comfort Zone classification.
    """)
    
    opt_btn = st.button("⚡ EXECUTE DESIGN OPTIMIZER", type="primary", use_container_width=True)
    
    if opt_btn or st.session_state.get("optimized_run", False):
        st.session_state["optimized_run"] = True
        
        best_cfg, curr_cfg, temp_diff, comfort_diff = opt_model.optimize(
            t_outdoor=t_outdoor,
            humidity=humidity,
            solar_exposure=solar_exposure,
            current_config={
                "roof": roof,
                "wall": wall,
                "ventilation": ventilation,
                "shading": shading,
                "size": shelter_size
            }
        )
        
        # Display side-by-side BEFORE vs AFTER cards (including zones and metrics)
        col_b1, col_b2 = st.columns(2)
        
        curr_theme = COLOR_THEME[curr_cfg['comfort_status']]
        best_theme = COLOR_THEME[best_cfg['comfort_status']]
        
        with col_b1:
            st.markdown(f"""
                <div style="border: 2px solid {curr_theme['border']}; padding: 20px; border-radius: 10px; background-color: rgba(22, 27, 34, 0.4);">
                    <h3 style="color: {curr_theme['hex']} !important; margin-top:0;">🛑 CURRENT SHELTER DESIGN</h3>
                    <p><b>Comfort Zone:</b> <span class="status-badge" style="background-color: {curr_theme['bg']}; color: {curr_theme['hex']}; border: 1px solid {curr_theme['border']}; padding: 2px 10px; font-size: 0.85rem;">{curr_cfg['comfort_status']}</span></p>
                    <p><b>Thermal Comfort Score:</b> {curr_cfg['comfort_score']:.1f}%</p>
                    <p><b>Estimated Indoor Temp:</b> {curr_cfg['t_indoor']:.1f}°C</p>
                    <hr style="border: 0; border-top: 1px solid #30363d; margin: 10px 0;">
                    <p><b>Roof Material:</b> {curr_cfg['roof']}</p>
                    <p><b>Wall Material:</b> {curr_cfg['wall']}</p>
                    <p><b>Ventilation Scheme:</b> {curr_cfg['ventilation']}</p>
                    <p><b>Shading Profile:</b> {curr_cfg['shading']}</p>
                    <p><b>Shelter Size:</b> {curr_cfg.get('size', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)
            
        with col_b2:
            st.markdown(f"""
                <div style="border: 2px solid {best_theme['border']}; padding: 20px; border-radius: 10px; background-color: rgba(22, 27, 34, 0.4); box-shadow: 0 0 15px {best_theme['hex']}30;">
                    <h3 style="color: {best_theme['hex']} !important; margin-top:0;">🏆 RECOMMENDED OPTIMAL DESIGN</h3>
                    <p><b>Comfort Zone:</b> <span class="status-badge" style="background-color: {best_theme['bg']}; color: {best_theme['hex']}; border: 1px solid {best_theme['border']}; padding: 2px 10px; font-size: 0.85rem;">{best_cfg['comfort_status']}</span></p>
                    <p><b>Thermal Comfort Score:</b> {best_cfg['comfort_score']:.1f}%</p>
                    <p><b>Estimated Indoor Temp:</b> {best_cfg['t_indoor']:.1f}°C</p>
                    <hr style="border: 0; border-top: 1px solid #30363d; margin: 10px 0;">
                    <p><b>Roof Material:</b> {best_cfg['roof']}</p>
                    <p><b>Wall Material:</b> {best_cfg['wall']}</p>
                    <p><b>Ventilation Scheme:</b> {best_cfg['ventilation']}</p>
                    <p><b>Shading Profile:</b> {best_cfg['shading']}</p>
                    <p><b>Shelter Size:</b> {best_cfg.get('size', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("### Improvement Delta Metrics")
        col_i1, col_i2, col_i3 = st.columns(3)
        with col_i1:
            st.metric(label="Temperature Variance Reduction", value=f"{temp_diff:.1f}°C", delta=f"{-temp_diff:.1f}°C", delta_color="inverse")
        with col_i2:
            st.metric(label="Comfort Index Gains", value=f"{best_cfg['comfort_score'] - curr_cfg['comfort_score']:.1f}%", delta=f"+{comfort_diff:.1f}%")
        with col_i3:
            st.metric(label="Comfort Zone Improvement", value=f"{curr_cfg['comfort_status']} ➔ {best_cfg['comfort_status']}")
            
        # Comparison Bar Chart
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            name='Current configuration',
            x=['Indoor Temp (°C)', 'Comfort Score (%)'],
            y=[curr_cfg['t_indoor'], curr_cfg['comfort_score']],
            marker_color=curr_theme['hex']
        ))
        fig_comp.add_trace(go.Bar(
            name='Optimized configuration',
            x=['Indoor Temp (°C)', 'Comfort Score (%)'],
            y=[best_cfg['t_indoor'], best_cfg['comfort_score']],
            marker_color=best_theme['hex']
        ))
        fig_comp.update_layout(
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#c9d1d9'
        )
        st.plotly_chart(fig_comp, use_container_width=True)

# Render AI Engine tab
with tab_ml:
    st.subheader("🧠 Adaptive Machine Learning Module")
    st.markdown("""
    Model predictive controller designed for coefficient auto-calibration from experimental observation sensor sets.
    """)
    
    col_ml1, col_ml2 = st.columns([1, 1.2])
    
    with col_ml1:
        st.write("#### Model Controller")
        train_btn = st.button("⚙️ Fit Predictive & Calibrate Models", type="secondary", use_container_width=True)
        
        if train_btn:
            metrics = ml_module.train_predictive_comfort()
            calib = ml_module.calibrate_coefficients()
            
            st.success("Scikit-Learn ML models successfully trained!")
            st.write("**Training Summary Metrics:**")
            st.json(metrics)
            st.write("**Calibration Factor Outputs:**")
            st.json(calib)
            
            st.session_state["ml_calibrated"] = True
            st.session_state["calibrated_coeffs"] = calib
            
    with col_ml2:
        st.write("#### Predictive Inference Testing")
        if st.session_state.get("ml_calibrated", False):
            ml_roof = st.selectbox("ML Input - Roof", [0, 1, 2], format_func=lambda x: ["Metal", "Reflective Metal", "Insulated Panel"][x])
            ml_wall = st.selectbox("ML Input - Wall", [0, 1, 2], format_func=lambda x: ["Metal", "Reflective Metal", "Insulated Panel"][x])
            ml_vent = st.selectbox("ML Input - Vent", [0, 1, 2], format_func=lambda x: ["Poor", "Moderate", "Good"][x])
            
            test_x = pd.DataFrame({
                "t_outdoor": [t_outdoor],
                "humidity": [humidity],
                "roof_code": [ml_roof],
                "wall_code": [ml_wall],
                "vent_code": [ml_vent]
            })
            pred_val = ml_module.temp_model.predict(test_x)[0]
            st.info(f"**RandomForest Regression prediction:** estimated observed indoor temp = `{pred_val:.2f}°C`")
        else:
            st.warning("Train models to unlock inferences using experimental coefficients.")

# Render Assumptions Tab
with tab_assumptions:
    st.subheader("Operational Framework Documentation & Assumptions")
    
    st.markdown("""
    ### 🔬 Scientific Honesty Declaration
    *   **Coefficient Status:** The current temperature contributions are **prototype coefficient variables** designed for modeling and system demonstration. They should not be used as raw physical material constants without experimental laboratory context.
    *   **Calibration Target:** In a production context, these coefficients would be adjusted dynamically using physical telemetry streams from our sensor interface module, mapping back through localized regression models.
    *   **Safety Indexing:** The thermal comfort score model is a normalized index based on typical human metabolic guidelines, intended for military deployment risk assessment (DRDO application contexts).
    
    ### ⚙️ System Architecture Flow
    """)
    
    st.markdown("""
    ```
    +--------------------------------------------------------+
    |                    ENVIRONMENT FEED                    |
    |  - IoT Sensor Telemetry (ESP32 Serial/MQTT)           |
    |  - Manual UI Forms (Simulation controls)               |
    +---------------------------+----------------------------+
                                |
                                v
    +--------------------------------------------------------+
    |                  THERMAL COEFF ENGINE                  |
    |  - Coefficients Lookup (shelter_coefficients.json)      |
    |  - Linear Model Calculator                             |
    +---------------------------+----------------------------+
                                |
                                v
    +--------------------------------------------------------+
    |                 THERMAL COMFORT ENGINE                 |
    |  - Trapezoidal Comfort Scoring                         |
    |  - Heat Index / Humidity Adjustment Penalty           |
    +---------------------------+----------------------------+
                                |
                                v
    +--------------------------------------------------------+
    |                 RECOMMENDATION ROUTER                  |
    |  - Problem Classifier & Prioritizer                    |
    |  - Design Configuration Permutations Grid Optimizer    |
    +--------------------------------------------------------+
    ```
    """)
    
    st.markdown("""
    ### ⚖️ Coefficient Reference Table
    """)
    st.json(thermal_model.coefficients)
