import os
import sys
from pathlib import Path
import streamlit as st
from PIL import Image

# Add root directory to python module search path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

from src.utils.config import Config
from src.inference.pipeline import get_inference_pipeline
from src.knowledge.disease_kb import get_knowledge_base
from src.severity.estimator import estimate_severity
from src.weather.service import get_weather_service
from src.risk_engine.engine import compute_risk

# ── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crop Disease Intelligence Platform",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.main-header {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    padding: 28px 32px;
    border-radius: 16px;
    color: white;
    margin-bottom: 28px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
.main-header h1 {
    color: #ffffff;
    font-weight: 700;
    margin: 0;
    font-size: 2.1rem;
    letter-spacing: -0.5px;
}
.main-header p {
    color: #b0c4d8;
    margin-top: 8px;
    margin-bottom: 0;
    font-size: 1.0rem;
}
.intel-card {
    background: linear-gradient(145deg, #ffffff, #f8fafc);
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.intel-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.10);
}
.intel-card .card-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin-bottom: 4px;
}
.intel-card .card-value {
    font-size: 1.55rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.2;
}
.intel-card .card-sub {
    font-size: 0.82rem;
    color: #94a3b8;
    margin-top: 4px;
}
/* Risk level colour coding */
.risk-low    { border-left: 5px solid #22c55e; }
.risk-medium { border-left: 5px solid #f59e0b; }
.risk-high   { border-left: 5px solid #ef4444; }
.risk-critical { border-left: 5px solid #7c3aed; }
/* Severity colour coding */
.sev-low      { border-left: 5px solid #22c55e; }
.sev-moderate { border-left: 5px solid #f59e0b; }
.sev-high     { border-left: 5px solid #ef4444; }
.sev-unknown  { border-left: 5px solid #94a3b8; }
/* Disease card */
.disease-card {
    border-left: 5px solid #3b82f6;
}
.disease-healthy {
    border-left: 5px solid #22c55e;
}
/* Factor badge */
.factor-badge {
    display: inline-block;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.82rem;
    color: #334155;
    margin: 4px 4px 4px 0;
    line-height: 1.4;
}
/* Weather grid */
.weather-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin-top: 8px;
}
.weather-cell {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 10px 14px;
    text-align: center;
}
.weather-cell .wc-icon { font-size: 1.4rem; }
.weather-cell .wc-val  { font-size: 1.1rem; font-weight: 600; color: #0f172a; }
.weather-cell .wc-lbl  { font-size: 0.72rem; color: #94a3b8; margin-top: 2px; }
/* Disclaimer */
.disclaimer-box {
    background: #fafafa;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 14px 18px;
    margin-top: 20px;
    font-size: 0.84rem;
    color: #6b7280;
    line-height: 1.5;
}
/* Prototype label */
.proto-badge {
    display: inline-block;
    background: #fff7ed;
    color: #c2410c;
    border: 1px solid #fed7aa;
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-left: 8px;
    vertical-align: middle;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: Risk level → CSS class and emoji ─────────────────────────────────
def risk_style(level: str):
    return {
        "Low":      ("risk-low",      "🟢"),
        "Medium":   ("risk-medium",   "🟡"),
        "High":     ("risk-high",     "🔴"),
        "Critical": ("risk-critical", "🟣"),
    }.get(level, ("risk-medium", "⚠️"))


def severity_style(level: str):
    return {
        "Low":      ("sev-low",      "🟢"),
        "Moderate": ("sev-moderate", "🟡"),
        "High":     ("sev-high",     "🔴"),
        "Unknown":  ("sev-unknown",  "⚪"),
    }.get(level, ("sev-unknown", "⚪"))


# ── Main Application ─────────────────────────────────────────────────────────
def main():
    # ── Sidebar ──────────────────────────────────────────────────────────────
    st.sidebar.image("https://img.icons8.com/color/96/tomato.png", width=72)
    st.sidebar.title("Crop Intelligence")
    st.sidebar.markdown("**Target Crop**: Tomato (`Solanum lycopersicum`)")

    st.sidebar.markdown("---")
    st.sidebar.subheader("📍 Location (Optional)")
    city_input = st.sidebar.text_input(
        "City name",
        placeholder="e.g. Mumbai, Nairobi, London",
        help="Used for live weather context. Requires OPENWEATHER_API_KEY in environment."
    )

    weather_svc = get_weather_service()
    if city_input and not weather_svc.is_configured:
        st.sidebar.warning("⚠️ OPENWEATHER_API_KEY not set — weather context disabled.")

    st.sidebar.markdown("---")
    st.sidebar.subheader("🌱 Growth Stage (Optional)")
    growth_stage = st.sidebar.selectbox(
        "Crop growth stage",
        options=["(not specified)", "seedling", "vegetative", "flowering", "fruiting", "ripening"],
        help="Affects contextual risk scoring."
    )
    if growth_stage == "(not specified)":
        growth_stage = None

    st.sidebar.markdown("---")
    st.sidebar.subheader("Supported Classes")
    for cls_name in Config.TARGET_CLASSES:
        st.sidebar.markdown(f"- `{cls_name}`")

    st.sidebar.markdown("---")
    st.sidebar.info("Backbone: **MobileNetV2** (ImageNet Transfer Learning)")
    st.sidebar.caption(
        "⚗️ Severity and risk scores are **prototype estimates** — "
        "not scientifically validated. See disclaimers in results."
    )

    # ── Main Header ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="main-header">
        <h1>🌱 AI Crop Disease Intelligence Platform</h1>
        <p>Upload a clear leaf photo to diagnose crop health, estimate disease severity,
           and view contextual risk assessment.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Upload Section ───────────────────────────────────────────────────────
    col_upload, col_preview = st.columns([1, 1])

    with col_upload:
        st.subheader("1. Upload Leaf Image")
        uploaded_file = st.file_uploader(
            "Choose a crop leaf image (JPG, PNG, WEBP)...",
            type=["jpg", "jpeg", "png", "webp"],
            help="Select a clear, close-up photo of the tomato leaf."
        )
        analyze_btn = st.button(
            "🔍 Analyze Crop Health",
            use_container_width=True,
            type="primary",
            disabled=(uploaded_file is None)
        )

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file).convert("RGB")
            with col_preview:
                st.subheader("2. Image Preview")
                st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_column_width=True)
        except Exception as e:
            st.error(f"Error reading image file: {str(e)}")
            return

        if analyze_btn:
            st.markdown("---")
            st.subheader("3. Diagnostic Results & Insights")

            with st.spinner("Running deep learning pipeline + contextual analysis…"):
                # 1. Read bytes for reuse
                uploaded_file.seek(0)
                image_bytes = uploaded_file.read()

                # 2. Inference
                try:
                    pipeline = get_inference_pipeline()
                    result = pipeline.predict(image_bytes)
                except Exception as err:
                    st.error(f"Inference failure: {str(err)}")
                    return

                kb = get_knowledge_base()
                disease_info = kb.get_disease_info(result["predicted_disease"])

                # 3. Severity
                severity_data = estimate_severity(image_bytes, result["predicted_disease"])

                # 4. Weather (if city provided and key configured)
                weather_data = None
                if city_input and weather_svc.is_configured:
                    weather_data = weather_svc.get_weather_by_city(city_input)
                    if not weather_data.get("weather_available"):
                        st.warning(
                            f"⛅ Weather fetch failed: {weather_data.get('error', 'Unknown error')}. "
                            "Continuing without weather context."
                        )
                        weather_data = None

                # 5. Risk
                risk_data = compute_risk(
                    disease=result["predicted_disease"],
                    confidence=result["confidence"],
                    severity_pct=severity_data.get("affected_area_percentage"),
                    temperature_c=weather_data.get("temperature_c") if weather_data else None,
                    humidity_pct=weather_data.get("humidity_pct") if weather_data else None,
                    rainfall_mm=weather_data.get("rainfall_mm") if weather_data else None,
                    growth_stage=growth_stage,
                )

            # ── Result Row 1: Disease + Confidence + Severity + Risk ─────────
            predicted = result["predicted_disease"]
            conf = result["confidence"]
            is_healthy = (predicted == "Healthy")

            disease_css = "disease-healthy" if is_healthy else "disease-card"
            disease_icon = "✅" if is_healthy else "⚠️"

            sev_level = severity_data.get("severity", "Unknown")
            sev_pct = severity_data.get("affected_area_percentage")
            sev_css, sev_emoji = severity_style(sev_level)

            risk_level = risk_data.get("risk_level", "Unknown")
            risk_score = risk_data.get("risk_score", 0.0)
            risk_css, risk_emoji = risk_style(risk_level)

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.markdown(f"""
                <div class="intel-card {disease_css}">
                    <div class="card-label">🦠 Disease</div>
                    <div class="card-value">{disease_icon} {predicted}</div>
                    <div class="card-sub">{disease_info.get('scientific_name', '')}</div>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                <div class="intel-card">
                    <div class="card-label">📊 Confidence</div>
                    <div class="card-value">{conf * 100:.1f}%</div>
                    <div class="card-sub">Model prediction certainty</div>
                </div>
                """, unsafe_allow_html=True)

            with c3:
                sev_pct_str = f"{sev_pct:.1f}%" if sev_pct is not None else "N/A"
                st.markdown(f"""
                <div class="intel-card {sev_css}">
                    <div class="card-label">🔬 Severity <span class="proto-badge">PROTOTYPE</span></div>
                    <div class="card-value">{sev_emoji} {sev_level}</div>
                    <div class="card-sub">~{sev_pct_str} affected area (heuristic)</div>
                </div>
                """, unsafe_allow_html=True)

            with c4:
                st.markdown(f"""
                <div class="intel-card {risk_css}">
                    <div class="card-label">⚠️ Risk Level <span class="proto-badge">PROTOTYPE</span></div>
                    <div class="card-value">{risk_emoji} {risk_level}</div>
                    <div class="card-sub">Score: {risk_score:.2f} / 1.00</div>
                </div>
                """, unsafe_allow_html=True)

            # ── Confidence progress bar ──────────────────────────────────────
            st.progress(min(max(conf, 0.0), 1.0), text=f"Prediction confidence: {conf*100:.1f}%")

            # ── Row 2: Probability chart + Weather ──────────────────────────
            chart_col, weather_col = st.columns([1.2, 1])

            with chart_col:
                st.markdown("**Class Probability Distribution**")
                st.bar_chart(result["class_probabilities"])

            with weather_col:
                if weather_data and weather_data.get("weather_available"):
                    loc = f"{weather_data.get('location_name', '')}, {weather_data.get('country', '')}".strip(", ")
                    st.markdown(f"**🌤️ Weather — {loc}**")
                    st.markdown(f"""
                    <div class="weather-grid">
                        <div class="weather-cell">
                            <div class="wc-icon">🌡️</div>
                            <div class="wc-val">{weather_data.get('temperature_c', '—'):.1f}°C</div>
                            <div class="wc-lbl">Temperature</div>
                        </div>
                        <div class="weather-cell">
                            <div class="wc-icon">💧</div>
                            <div class="wc-val">{weather_data.get('humidity_pct', '—')}%</div>
                            <div class="wc-lbl">Humidity</div>
                        </div>
                        <div class="weather-cell">
                            <div class="wc-icon">🌧️</div>
                            <div class="wc-val">{weather_data.get('rainfall_mm', 0.0):.1f} mm</div>
                            <div class="wc-lbl">Rainfall (1h)</div>
                        </div>
                        <div class="weather-cell">
                            <div class="wc-icon">💨</div>
                            <div class="wc-val">{weather_data.get('wind_speed_ms', '—')} m/s</div>
                            <div class="wc-lbl">Wind Speed</div>
                        </div>
                        <div class="weather-cell" style="grid-column: span 2;">
                            <div class="wc-icon">⛅</div>
                            <div class="wc-val">{weather_data.get('condition', '—')}</div>
                            <div class="wc-lbl">{weather_data.get('description', '')}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                elif city_input:
                    st.info("⛅ Weather data unavailable. Ensure city name is correct and API key is set.")
                else:
                    st.info("📍 Enter a city in the sidebar to add live weather context to the risk assessment.")

            # ── Risk Factors ─────────────────────────────────────────────────
            st.markdown("---")
            factors = risk_data.get("factors", [])
            if factors:
                st.markdown(f"**{risk_emoji} Risk Factors** (Score: `{risk_score:.2f}` — Level: `{risk_level}`)")
                badges_html = "".join(
                    f'<span class="factor-badge">• {f}</span>' for f in factors
                )
                st.markdown(f'<div style="margin-top:8px">{badges_html}</div>', unsafe_allow_html=True)
            else:
                st.markdown("**✅ No significant risk factors detected.**")

            # ── Detailed Knowledge Tabs ───────────────────────────────────────
            st.markdown("---")
            tab_symptoms, tab_causes, tab_prevention = st.tabs([
                "📋 Symptoms",
                "🌡️ Causes & Conditions",
                "🛡️ Preventive & Management"
            ])

            with tab_symptoms:
                st.markdown("#### Observed Symptoms")
                for symptom in disease_info.get("symptoms", []):
                    st.markdown(f"- {symptom}")

            with tab_causes:
                st.markdown("#### Primary Pathogen & Causes")
                for cause in disease_info.get("general_causes", []):
                    st.markdown(f"- {cause}")
                st.markdown("#### Favorable Environmental Conditions")
                for cond in disease_info.get("favorable_conditions", []):
                    st.markdown(f"- {cond}")

            with tab_prevention:
                st.markdown("#### Recommended Preventive Measures")
                for prev in disease_info.get("preventive_measures", []):
                    st.markdown(f"- {prev}")
                st.markdown("#### General Field Management Practices")
                for mgt in disease_info.get("general_management_practices", []):
                    st.markdown(f"- {mgt}")

            # ── Disclaimers ───────────────────────────────────────────────────
            st.markdown(f"""
            <div class="disclaimer-box">
                <b>⚖️ Agricultural Disclaimer:</b><br/>
                {disease_info.get('disclaimer', '')}<br/><br/>
                <b>⚗️ Prototype Notice (Severity & Risk):</b><br/>
                {severity_data.get('prototype_disclaimer', '')}
                <br/>
                {risk_data.get('disclaimer', '')}
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
