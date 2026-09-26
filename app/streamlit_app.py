import os
import sys
import io
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

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

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

# ── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Crop Disease & Pest Intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS (Glassmorphism & Clean Typography) ─────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.main-header {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    padding: 26px 32px;
    border-radius: 16px;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.18);
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
    margin-top: 6px;
    margin-bottom: 0;
    font-size: 1.0rem;
}
.intel-card {
    background: linear-gradient(145deg, #ffffff, #f8fafc);
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.intel-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.09);
}
.intel-card .card-label {
    font-size: 0.76rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin-bottom: 4px;
}
.intel-card .card-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.2;
}
.intel-card .card-sub {
    font-size: 0.82rem;
    color: #94a3b8;
    margin-top: 4px;
}

/* Alert Cards */
.alert-card-active {
    background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    border: 2px solid #ef4444;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 16px rgba(239, 68, 68, 0.15);
}
.alert-card-active h3 {
    color: #991b1b;
    margin: 0 0 8px 0;
    font-size: 1.3rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 8px;
}
.alert-card-inactive {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    border: 1px solid #86efac;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 20px;
    color: #166534;
    font-weight: 500;
}

/* Risk level colour coding */
.risk-low      { border-left: 5px solid #22c55e; }
.risk-medium   { border-left: 5px solid #f59e0b; }
.risk-high     { border-left: 5px solid #ef4444; }
.risk-critical { border-left: 5px solid #7c3aed; }

/* Severity colour coding */
.sev-low      { border-left: 5px solid #22c55e; }
.sev-moderate { border-left: 5px solid #f59e0b; }
.sev-high     { border-left: 5px solid #ef4444; }
.sev-unknown  { border-left: 5px solid #94a3b8; }

/* Disease card */
.disease-card   { border-left: 5px solid #3b82f6; }
.disease-healthy { border-left: 5px solid #22c55e; }
.disease-uncertain { border-left: 5px solid #f97316; background: #fff7ed; }

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

/* Recommendation Card */
.rec-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.rec-category {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #0284c7;
    margin-bottom: 4px;
}
.rec-message {
    font-size: 0.92rem;
    color: #1e293b;
    line-height: 1.5;
}
.rec-source {
    font-size: 0.74rem;
    color: #64748b;
    margin-top: 6px;
    font-style: italic;
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
.weather-cell .wc-icon { font-size: 1.3rem; }
.weather-cell .wc-val  { font-size: 1.05rem; font-weight: 600; color: #0f172a; }
.weather-cell .wc-lbl  { font-size: 0.72rem; color: #94a3b8; margin-top: 2px; }

/* Disclaimer box */
.disclaimer-box {
    background: #fafafa;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 14px 18px;
    margin-top: 20px;
    font-size: 0.82rem;
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
    padding: 2px 7px;
    font-size: 0.70rem;
    font-weight: 600;
    margin-left: 6px;
    vertical-align: middle;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: Style maps ───────────────────────────────────────────────────────
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


def draw_pest_bounding_boxes(image: Image.Image, pests: List[Dict[str, Any]]) -> Image.Image:
    """Draw bounding boxes and labels for detected pests on a copy of the image."""
    if not pests:
        return image

    annotated = image.copy().convert("RGB")
    draw = ImageDraw.Draw(annotated)

    for p in pests:
        box = p.get("bounding_box", [])
        if len(box) == 4:
            x1, y1, x2, y2 = box
            pest_name = p.get("pest", "Pest")
            conf = p.get("confidence", 0.0)

            # Draw outer rectangle
            draw.rectangle([x1, y1, x2, y2], outline="#ef4444", width=3)

            # Draw label background and text
            label = f"{pest_name} ({conf * 100:.1f}%)"
            draw.rectangle([x1, max(0, y1 - 18), x1 + len(label) * 8 + 8, y1], fill="#ef4444")
            draw.text((x1 + 4, max(0, y1 - 16)), label, fill="#ffffff")

    return annotated


def check_backend_health() -> Dict[str, Any]:
    """Query FastAPI /health endpoint."""
    try:
        res = requests.get(f"{API_BASE_URL}/health", timeout=3)
        if res.status_code == 200:
            return {"reachable": True, "data": res.json()}
        return {"reachable": False, "error": f"HTTP {res.status_code}"}
    except Exception as e:
        return {"reachable": False, "error": str(e)}


# ── Main Application ─────────────────────────────────────────────────────────
def main():
    # Initialize in-memory session history if not already present
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []

    # ── Sidebar ──────────────────────────────────────────────────────────────
    st.sidebar.image("https://img.icons8.com/color/96/tomato.png", width=68)
    st.sidebar.title("Farmer Dashboard")
    st.sidebar.markdown("**Target Crop**: Tomato (`Solanum lycopersicum`)")

    # Backend Connection Status
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔌 Backend Connection")
    health_info = check_backend_health()
    if health_info["reachable"]:
        st.sidebar.success(f"Connected to API (`{API_BASE_URL}`)")
        api_data = health_info["data"]
        pest_status_txt = "Ready" if api_data.get("pest_model_available") else "Weights Required"
        st.sidebar.caption(f"API v{api_data.get('version')} | Weather: {'Active' if api_data.get('weather_configured') else 'Disabled'} | Pest Model: {pest_status_txt}")
    else:
        st.sidebar.error(f"API Unreachable at `{API_BASE_URL}`")
        st.sidebar.caption("Run `uvicorn api.main:app --port 8000` to start the backend.")

    # Location (Optional)
    st.sidebar.markdown("---")
    st.sidebar.subheader("📍 Location (Optional)")
    city_input = st.sidebar.text_input(
        "City name",
        placeholder="e.g. Mumbai, Nairobi, London",
        help="Used for live weather context and risk assessment."
    )

    # Growth Stage (Optional)
    st.sidebar.markdown("---")
    st.sidebar.subheader("🌱 Growth Stage (Optional)")
    growth_stage = st.sidebar.selectbox(
        "Crop growth stage",
        options=["(not specified)", "seedling", "vegetative", "flowering", "fruiting", "ripening"],
        help="Affects contextual risk scoring (e.g. flowering/fruiting stages are more vulnerable)."
    )
    if growth_stage == "(not specified)":
        growth_stage = None

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "⚗️ **Notice**: Severity and risk ratings are prototype decision-support estimates. "
        "Pest detection requires local YOLO weights configuration."
    )

    # ── Main Header ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="main-header">
        <h1>🌱 AI Crop Disease & Pest Intelligence Platform</h1>
        <p>Comprehensive crop health diagnostics: disease classification, pest detection,
           severity estimation, live weather risk assessment, and actionable agricultural advice.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Section 1: Upload & Image Preview ────────────────────────────────────
    col_upload, col_preview = st.columns([1.1, 0.9])

    with col_upload:
        st.subheader("1. Upload Crop Image")
        uploaded_file = st.file_uploader(
            "Choose a crop leaf photo (JPG, PNG, WEBP)...",
            type=["jpg", "jpeg", "png", "webp"],
            help="For best accuracy, take a clear, well-lit photo of the affected leaf."
        )

        analyze_btn = st.button(
            "🔍 Analyze Crop Health",
            use_container_width=True,
            type="primary",
            disabled=(uploaded_file is None)
        )

    image_obj = None
    if uploaded_file is not None:
        try:
            image_obj = Image.open(uploaded_file).convert("RGB")
            with col_preview:
                st.subheader("2. Image Preview")
                st.image(image_obj, caption=f"Selected: {uploaded_file.name}", use_column_width=True)
        except Exception as e:
            st.error(f"Unable to read image file: {str(e)}")
            return

    # ── Section 2: Analysis Execution ────────────────────────────────────────
    if uploaded_file is not None and analyze_btn:
        st.markdown("---")

        with st.spinner("Analyzing image through AI intelligence pipeline..."):
            uploaded_file.seek(0)
            image_bytes = uploaded_file.read()

            # Execute HTTP Request to FastAPI /predict
            try:
                params = {}
                if city_input:
                    params["city"] = city_input
                if growth_stage:
                    params["growth_stage"] = growth_stage

                files = {"file": (uploaded_file.name, image_bytes, uploaded_file.type or "image/jpeg")}
                response = requests.post(f"{API_BASE_URL}/predict", params=params, files=files, timeout=30)

                if response.status_code == 200:
                    report = response.json()
                elif response.status_code == 400:
                    st.error(f"Invalid image request: {response.json().get('detail', 'Bad Request')}")
                    return
                elif response.status_code == 503:
                    st.error("Service Unavailable: Machine learning model checkpoints are missing on the backend.")
                    return
                else:
                    st.error(f"Server error ({response.status_code}): {response.text}")
                    return

            except requests.exceptions.ConnectionError:
                st.error(
                    f"⚠️ Unable to connect to backend at `{API_BASE_URL}`. "
                    "Please ensure the FastAPI service is running (`uvicorn api.main:app --port 8000`)."
                )
                return
            except requests.exceptions.Timeout:
                st.error("⏱️ Analysis timed out. The server took too long to process the image.")
                return
            except Exception as err:
                st.error(f"An unexpected error occurred: {str(err)}")
                return

        # Store in session history
        disease_obj = report.get("disease", {})
        severity_obj = report.get("severity", {})
        risk_obj = report.get("risk", {})
        pests_list = report.get("pests", [])
        
        # Extract prediction status
        prediction_status = disease_obj.get("prediction_status", "UNKNOWN")
        status_message = disease_obj.get("status_message", "")

        st.session_state.analysis_history.insert(0, {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filename": uploaded_file.name,
            "disease": disease_obj.get("name") or "Uncertain",
            "confidence": disease_obj.get("confidence", 0.0),
            "prediction_status": prediction_status,
            "severity": severity_obj.get("level") or "N/A",
            "risk_level": risk_obj.get("risk_level", "Unknown"),
            "risk_score": risk_obj.get("risk_score", 0.0),
            "pests_count": len(pests_list),
        })
        
        # ── UNCERTAINTY WARNING BANNER (if diagnosis uncertain) ────────────────
        if prediction_status in ["UNSUPPORTED_OR_UNCERTAIN", "INVALID_IMAGE"]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); 
                        border-left: 5px solid #f59e0b; 
                        padding: 20px 24px; 
                        border-radius: 12px; 
                        margin-bottom: 24px;
                        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.15);">
                <h3 style="color: #92400e; margin: 0 0 12px 0; font-size: 1.3rem;">
                    ⚠️ Diagnosis Uncertain
                </h3>
                <p style="color: #78350f; margin: 0 0 8px 0; font-size: 1.05rem; font-weight: 500;">
                    {status_message}
                </p>
                <p style="color: #92400e; margin: 0; font-size: 0.95rem;">
                    <strong>What to do:</strong> Upload clearer images with better lighting, 
                    focus on symptomatic leaf areas, or consult a local agricultural extension agent 
                    for professional diagnosis.
                </p>
            </div>
            """, unsafe_allow_html=True)

        # ── 1. Alert Banner (Prominent at top) ───────────────────────────────
        alert_obj = report.get("alert", {})
        if alert_obj.get("active"):
            sev_badge = alert_obj.get("severity", "High")
            reasons_html = "".join(f"<li>{r}</li>" for r in alert_obj.get("reasons", []))
            st.markdown(f"""
            <div class="alert-card-active">
                <h3>🚨 {alert_obj.get('title', 'Crop Health Alert')}</h3>
                <p style="margin-bottom:8px; font-weight:600; color:#b91c1c;">
                    Immediate attention recommended. Contributing alert reasons:
                </p>
                <ul style="margin:0; padding-left:20px; color:#7f1d1d;">
                    {reasons_html}
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-card-inactive">
                🟢 <b>No active high-risk alert.</b> Crop health conditions are within manageable parameters.
            </div>
            """, unsafe_allow_html=True)

        # ── 2. Crop Health Summary Metrics ───────────────────────────────────
        st.subheader("3. Crop Health Report")

        disease_name = disease_obj.get("name") or "Uncertain"
        conf_val = disease_obj.get("confidence", 0.0)
        is_healthy = (disease_name == "Healthy")
        is_uncertain = prediction_status in ["UNSUPPORTED_OR_UNCERTAIN", "INVALID_IMAGE"]

        # Dynamic styling based on status
        if is_uncertain:
            disease_css = "disease-uncertain"
            disease_icon = "❓"
            confidence_style = "background: #fff7ed; border: 2px solid #fed7aa;"
        elif is_healthy:
            disease_css = "disease-healthy"
            disease_icon = "✅"
            confidence_style = ""
        else:
            disease_css = "disease-card"
            disease_icon = "⚠️"
            confidence_style = ""

        sev_level = severity_obj.get("level") or "N/A"
        sev_pct = severity_obj.get("visible_affected_area_percentage")
        sev_status = severity_obj.get("status", "UNAVAILABLE")
        sev_css, sev_emoji = severity_style(sev_level) if sev_level != "N/A" else ("sev-unknown", "⚪")

        risk_level = risk_obj.get("risk_level", "Unknown")
        risk_score = risk_obj.get("risk_score", 0.0)
        risk_css, risk_emoji = risk_style(risk_level)

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            disease_display = disease_name if not is_uncertain else "Uncertain"
            sci_name = disease_obj.get('scientific_name') if not is_uncertain else "Diagnosis unavailable"
            st.markdown(f"""
            <div class="intel-card {disease_css}">
                <div class="card-label">🦠 Disease</div>
                <div class="card-value">{disease_icon} {disease_display}</div>
                <div class="card-sub">{sci_name or 'Tomato Pathogen'}</div>
                {'<div class="proto-badge" style="margin-top: 8px;">UNCERTAIN</div>' if is_uncertain else ''}
            </div>
            """, unsafe_allow_html=True)

        with c2:
            conf_display = f"{conf_val * 100:.1f}%"
            conf_label = "Model confidence" if not is_uncertain else "⚠️ Below threshold"
            st.markdown(f"""
            <div class="intel-card" style="{confidence_style}">
                <div class="card-label">📊 Confidence</div>
                <div class="card-value">{conf_display}</div>
                <div class="card-sub">{conf_label}</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            # Handle new severity format with status
            if sev_status == "UNRELIABLE":
                sev_display = "Unreliable"
                sev_pct_str = "Diagnosis uncertain"
                sev_badge = "UNRELIABLE"
            elif sev_status == "UNAVAILABLE":
                sev_display = "Unavailable"
                sev_pct_str = "Analysis unavailable"
                sev_badge = "N/A"
            else:
                sev_display = sev_level
                sev_pct_str = f"~{sev_pct:.1f}% affected" if sev_pct is not None else "N/A"
                sev_badge = "PROTOTYPE"
            
            st.markdown(f"""
            <div class="intel-card {sev_css}">
                <div class="card-label">🔬 Severity <span class="proto-badge">{sev_badge}</span></div>
                <div class="card-value">{sev_emoji} {sev_display}</div>
                <div class="card-sub">{sev_pct_str}</div>
            </div>
            """, unsafe_allow_html=True)

        with c4:
            # Check if risk assessment has insufficient data
            risk_status = risk_obj.get("status", "AVAILABLE")
            if risk_status == "INSUFFICIENT_DATA":
                risk_display = "Insufficient Data"
                risk_sub = "Confident diagnosis required"
                risk_badge = "UNAVAILABLE"
            else:
                risk_display = risk_level
                risk_sub = f"Risk Score: {risk_score:.2f} / 1.00"
                risk_badge = "PROTOTYPE"
            
            st.markdown(f"""
            <div class="intel-card {risk_css}">
                <div class="card-label">⚠️ Risk Level <span class="proto-badge">{risk_badge}</span></div>
                <div class="card-value">{risk_emoji} {risk_display}</div>
                <div class="card-sub">{risk_sub}</div>
            </div>
            """, unsafe_allow_html=True)

        # Confidence Bar
        st.progress(min(max(conf_val, 0.0), 1.0), text=f"Diagnostic confidence: {conf_val * 100:.1f}%")

        # ── 3. Pest Detection & Visualization ────────────────────────────────
        st.markdown("---")
        st.subheader("4. Pest Detection")

        col_pest_vis, col_pest_info = st.columns([1, 1])

        if pests_list:
            annotated_img = draw_pest_bounding_boxes(image_obj, pests_list)
            with col_pest_vis:
                st.image(annotated_img, caption="Annotated Pest Detections", use_column_width=True)

            with col_pest_info:
                st.markdown(f"**Found {len(pests_list)} pest instance(s):**")
                for idx, p in enumerate(pests_list, 1):
                    p_name = p.get("pest", "Pest")
                    p_conf = p.get("confidence", 0.0)
                    p_box = p.get("bounding_box", [])
                    st.markdown(f"- **{p_name}** — Confidence: `{p_conf * 100:.1f}%` (Box: `{p_box}`)")
        else:
            with col_pest_vis:
                st.image(image_obj, caption="Uploaded Image", use_column_width=True)

            with col_pest_info:
                # Check backend pest availability
                pest_configured = health_info.get("data", {}).get("pest_model_available", False)
                if pest_configured:
                    st.info("✅ No pests detected in the submitted leaf image.")
                else:
                    st.warning(
                        "ℹ️ **Pest detection model is not currently configured.**\n\n"
                        "To enable pest bounding boxes, place trained YOLOv8 weights at `src/models/pest_detection/weights/pest_yolov8.pt`. "
                        "The platform runs safely in disease-only mode without displaying fabricated pest results."
                    )

        # ── 4. Weather & Environmental Context ───────────────────────────────
        st.markdown("---")
        st.subheader("5. Weather & Environmental Context")

        weather_obj = report.get("weather")
        if weather_obj and weather_obj.get("weather_available"):
            loc_str = f"{weather_obj.get('location_name', '')}, {weather_obj.get('country', '')}".strip(", ")
            st.markdown(f"**📍 Location: {loc_str}**")
            st.markdown(f"""
            <div class="weather-grid">
                <div class="weather-cell">
                    <div class="wc-icon">🌡️</div>
                    <div class="wc-val">{weather_obj.get('temperature_c', '—')}°C</div>
                    <div class="wc-lbl">Temperature</div>
                </div>
                <div class="weather-cell">
                    <div class="wc-icon">💧</div>
                    <div class="wc-val">{weather_obj.get('humidity_pct', '—')}%</div>
                    <div class="wc-lbl">Relative Humidity</div>
                </div>
                <div class="weather-cell">
                    <div class="wc-icon">🌧️</div>
                    <div class="wc-val">{weather_obj.get('rainfall_mm', 0.0)} mm</div>
                    <div class="wc-lbl">Rainfall (1h)</div>
                </div>
                <div class="weather-cell">
                    <div class="wc-icon">💨</div>
                    <div class="wc-val">{weather_obj.get('wind_speed_ms', '—')} m/s</div>
                    <div class="wc-lbl">Wind Speed</div>
                </div>
                <div class="weather-cell" style="grid-column: span 2;">
                    <div class="wc-icon">⛅</div>
                    <div class="wc-val">{weather_obj.get('condition', '—')}</div>
                    <div class="wc-lbl">{weather_obj.get('description', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("⛅ **Weather data unavailable.** Enter a valid city in the sidebar (requires `OPENWEATHER_API_KEY`) to enable live environmental risk context.")

        # ── 5. Risk Assessment Breakdown ─────────────────────────────────────
        st.markdown("---")
        st.subheader("6. Risk Assessment Breakdown")

        factors = risk_obj.get("factors", [])
        if factors:
            st.markdown(f"**Contributing Risk Factors** (Risk Level: `{risk_level}` — Index: `{risk_score:.2f}`):")
            badges_html = "".join(f'<span class="factor-badge">• {f}</span>' for f in factors)
            st.markdown(f'<div style="margin-top:6px; margin-bottom:12px;">{badges_html}</div>', unsafe_allow_html=True)
        else:
            st.markdown("✅ No elevated risk factors detected.")

        st.caption("⚗️ **Prototype Note**: Risk scoring combines model confidence, severity heuristics, and environmental bands as an informational decision-support aid.")

        # ── 6. Structured Agricultural Recommendations ───────────────────────
        st.markdown("---")
        st.subheader("7. Structured Agricultural Recommendations")

        recs = report.get("recommendations", [])
        if recs:
            for r in recs:
                cat = r.get("category", "General")
                msg = r.get("message", "")
                src = r.get("source")
                src_html = f'<div class="rec-source">📖 Source: {src}</div>' if src else ""

                st.markdown(f"""
                <div class="rec-card">
                    <div class="rec-category">{cat}</div>
                    <div class="rec-message">{msg}</div>
                    {src_html}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No specific recommendations generated. Follow standard crop care practices.")

        # ── 7. Detailed Disease Knowledge ────────────────────────────────────
        with st.expander("📖 Detailed Disease Knowledge & Symptoms Reference"):
            t1, t2, t3 = st.tabs(["Observed Symptoms", "Causes & Conditions", "General Prevention"])
            with t1:
                for s in disease_obj.get("symptoms", []):
                    st.markdown(f"- {s}")
            with t2:
                st.markdown("**Primary Causes:**")
                for c in disease_obj.get("general_causes", []):
                    st.markdown(f"- {c}")
                st.markdown("**Favorable Conditions:**")
                for f in disease_obj.get("favorable_conditions", []):
                    st.markdown(f"- {f}")
            with t3:
                for p in disease_obj.get("general_preventive_information", []):
                    st.markdown(f"- {p}")

        # ── 8. Disclaimers ───────────────────────────────────────────────────
        st.markdown(f"""
        <div class="disclaimer-box">
            <b>⚖️ Agricultural & AI Advisory Notice:</b><br/>
            • <b>Model Predictions:</b> AI predictions are probabilistic and may be incorrect. Always visually confirm with local field observations.<br/>
            • <b>Prototype Estimates:</b> Severity percentages and risk scores are heuristic prototype models, not certified epidemiological data.<br/>
            • <b>Expert Consultation:</b> This platform provides general decision-support guidance and does not replace the advice of certified local agronomists or agricultural extension officers.<br/>
            • <b>Treatment Safety:</b> Adhere strictly to regional regulations and manufacturer instructions before applying any agricultural treatments.
        </div>
        """, unsafe_allow_html=True)

    # ── Section 3: Previous Analyses (In-Memory Session History) ─────────────
    st.markdown("---")
    st.subheader("8. Previous Analyses (Session History)")

    if st.session_state.analysis_history:
        # History table
        history_data = []
        for item in st.session_state.analysis_history:
            history_data.append({
                "Timestamp": item["timestamp"],
                "Image": item["filename"],
                "Detected Disease": item["disease"],
                "Confidence": f"{item['confidence'] * 100:.1f}%",
                "Severity": item["severity"],
                "Risk Level": item["risk_level"],
                "Pests Found": item["pests_count"],
            })

        st.dataframe(history_data, use_container_width=True)

        if st.button("🗑️ Clear Analysis History"):
            st.session_state.analysis_history = []
            st.rerun()
    else:
        st.caption("No previous analyses in the current session. Upload and analyze an image to view history.")


if __name__ == "__main__":
    main()
