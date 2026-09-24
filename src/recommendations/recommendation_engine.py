"""Structured Agricultural Recommendation Engine.

Generates actionable, safety-first, non-chemical and IPM-focused agricultural
recommendations based on crop type, detected disease, severity level, detected pests,
environmental context (weather), and risk assessment.

Guiding Principles:
1. No fabricated chemical dosages, pesticide concentrations, or unsafe chemical instructions.
2. Promotes Integrated Pest Management (IPM), cultural controls, sanitation, and scouting.
3. Clearly references reputable agricultural extension sources where applicable.
4. Advises certified agronomist/extension consultation for elevated severity or critical risk.
"""

from typing import List, Dict, Any, Optional

# Reliable agricultural guidance database for diseases
DISEASE_RECOMMENDATIONS = {
    "Early Blight": [
        {
            "category": "Sanitation",
            "message": "Prune and safely discard lower infected leaves showing concentric lesions to reduce fungal inoculum. Disinfect pruning shears between plants.",
            "source": "University Agricultural Extension IPM Guidelines",
        },
        {
            "category": "Cultural Control",
            "message": "Apply organic mulch around the plant base to prevent soil-borne fungal spores from splashing onto lower foliage during rain or irrigation.",
            "source": "FAO Tomato Integrated Pest Management",
        },
        {
            "category": "Irrigation Management",
            "message": "Use drip irrigation or water at the soil level early in the morning so foliage dries quickly before nightfall.",
            "source": "University Agricultural Extension IPM Guidelines",
        },
        {
            "category": "Crop Rotation",
            "message": "Rotate tomato crops with non-solanaceous species (e.g., legumes, cereals, or brassicas) on a 2 to 3 year cycle to break the disease cycle.",
            "source": "USDA Plant Disease Management Handbook",
        },
    ],
    "Late Blight": [
        {
            "category": "Monitoring",
            "message": "Scout the field daily, especially during cool and humid periods. Check both leaf surfaces and stems for water-soaked lesions with white mold.",
            "source": "FAO Tomato Integrated Pest Management",
        },
        {
            "category": "Sanitation",
            "message": "Immediately remove and destroy severely infected whole plants to prevent rapid airborne spore transmission to neighboring healthy rows.",
            "source": "University Agricultural Extension IPM Guidelines",
        },
        {
            "category": "Cultural Control",
            "message": "Ensure maximum row spacing and trellis plants to facilitate canopy airflow and accelerate foliage drying.",
            "source": "USDA Plant Disease Management Handbook",
        },
        {
            "category": "Expert Consultation",
            "message": "Late Blight spreads rapidly under favorable conditions. Consult a licensed local agricultural extension officer immediately for region-approved protective management protocols.",
            "source": "National Agricultural Extension Service",
        },
    ],
    "Leaf Mold": [
        {
            "category": "Environmental Management",
            "message": "Improve greenhouse or tunnel ventilation and increase row spacing to reduce relative humidity below 80%.",
            "source": "University Agricultural Extension IPM Guidelines",
        },
        {
            "category": "Cultural Control",
            "message": "Prune excess suckers and lower foliage to promote vertical air circulation through the canopy.",
            "source": "FAO Tomato Integrated Pest Management",
        },
        {
            "category": "Irrigation Management",
            "message": "Avoid overhead sprinkler irrigation; keep watering strictly at root level to prevent prolonged leaf wetness.",
            "source": "USDA Plant Disease Management Handbook",
        },
    ],
    "Healthy": [
        {
            "category": "Maintenance",
            "message": "Continue standard crop management: maintain balanced soil nutrition, regular weed management, and consistent irrigation.",
            "source": "Standard Agricultural Good Practices",
        },
        {
            "category": "Preventive Scouting",
            "message": "Perform weekly scouting across different field quadrants to detect any early signs of pests or disease before outbreaks establish.",
            "source": "Integrated Pest Management Field Guide",
        },
    ],
}

# Reliable agricultural guidance database for pests
PEST_RECOMMENDATIONS = {
    "Aphid": [
        {
            "category": "Monitoring",
            "message": "Inspect the undersides of young leaves and growing tips for aphid colonies and honeydew secretions.",
            "source": "University Agricultural Extension IPM Guidelines",
        },
        {
            "category": "Biological Control",
            "message": "Encourage or introduce natural predators such as lady beetles, lacewing larvae, and hoverfly larvae in the canopy.",
            "source": "FAO Tomato Integrated Pest Management",
        },
        {
            "category": "Cultural Control",
            "message": "Use yellow sticky cards for monitoring population dynamics and wash light infestations off leaves with gentle water sprays.",
            "source": "University Agricultural Extension IPM Guidelines",
        },
    ],
    "Whitefly": [
        {
            "category": "Monitoring",
            "message": "Deploy yellow sticky traps at canopy height to monitor adult whitefly activity and detect early population surges.",
            "source": "FAO Tomato Integrated Pest Management",
        },
        {
            "category": "Physical Control",
            "message": "Use fine insect netting (50-mesh) on greenhouse vents or row covers in open fields to exclude adult whiteflies.",
            "source": "University Agricultural Extension IPM Guidelines",
        },
        {
            "category": "Biological Control",
            "message": "Conserve parasitic wasps (Encarsia formosa / Eretmocerus spp.) and predatory mites as natural biological control agents.",
            "source": "Integrated Pest Management Field Guide",
        },
    ],
    "Tomato Hornworm": [
        {
            "category": "Physical Control",
            "message": "Handpick hornworm caterpillars from foliage in the early morning or evening and transfer or destroy them.",
            "source": "University Agricultural Extension IPM Guidelines",
        },
        {
            "category": "Biological Control",
            "message": "If caterpillars carry small white silken cocoons on their backs, leave them in place; these are beneficial parasitoid Braconid wasps.",
            "source": "Integrated Pest Management Field Guide",
        },
    ],
    "Caterpillar": [
        {
            "category": "Monitoring",
            "message": "Check for chew marks on leaves and fruit, and look for frass (droppings) on lower leaves to pinpoint feeding caterpillars.",
            "source": "University Agricultural Extension IPM Guidelines",
        },
        {
            "category": "Physical Control",
            "message": "Hand-pick caterpillars where feasible on small plots, or use pheromone traps to monitor adult moth flight periods.",
            "source": "FAO Tomato Integrated Pest Management",
        },
    ],
    "Mite": [
        {
            "category": "Cultural Control",
            "message": "Maintain adequate soil moisture and reduce dust along field roadways, as dusty and dry conditions encourage spider mite outbreaks.",
            "source": "University Agricultural Extension IPM Guidelines",
        },
        {
            "category": "Biological Control",
            "message": "Conserve predatory phytoseiid mites by avoiding broad-spectrum synthetic chemical applications.",
            "source": "FAO Tomato Integrated Pest Management",
        },
    ],
}


def generate_recommendations(
    crop: str = "Tomato",
    disease: Optional[str] = None,
    pests: Optional[List[Dict[str, Any]]] = None,
    severity: Optional[Dict[str, Any]] = None,
    weather: Optional[Dict[str, Any]] = None,
    risk_level: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Generate structured agricultural recommendations based on comprehensive contextual cues.

    Parameters:
        crop: Target crop name (e.g., "Tomato").
        disease: Detected disease class name.
        pests: List of detected pest dictionaries with 'pest', 'confidence', 'bounding_box'.
        severity: Severity result dictionary (contains 'severity' or 'level', 'affected_area_percentage').
        weather: Weather observation dictionary (temperature, humidity, rainfall, etc.).
        risk_level: Overall computed risk level ("Low", "Medium", "High", "Critical").

    Returns:
        List of structured recommendation dicts:
        [{"category": "...", "message": "...", "source": "..."}]
    """
    recs: List[Dict[str, str]] = []
    seen_messages = set()

    def _add_rec(category: str, message: str, source: Optional[str] = None):
        if message not in seen_messages:
            seen_messages.add(message)
            item: Dict[str, str] = {"category": category, "message": message}
            if source:
                item["source"] = source
            recs.append(item)

    # 1. Disease-Specific Recommendations
    if disease and disease in DISEASE_RECOMMENDATIONS:
        for r in DISEASE_RECOMMENDATIONS[disease]:
            _add_rec(r["category"], r["message"], r.get("source"))
    elif disease and disease != "Healthy":
        _add_rec(
            "General Disease Management",
            f"For suspected {disease} on {crop}, remove heavily symptomatic foliage, improve plant spacing, and ensure clean tools.",
            "General Integrated Pest Management Principles",
        )

    # 2. Pest-Specific Recommendations
    if pests and isinstance(pests, list):
        detected_pests = {p.get("pest") for p in pests if isinstance(p, dict) and p.get("pest")}
        for pest_name in detected_pests:
            if pest_name in PEST_RECOMMENDATIONS:
                for r in PEST_RECOMMENDATIONS[pest_name]:
                    _add_rec(r["category"], r["message"], r.get("source"))
            else:
                _add_rec(
                    "Pest Management",
                    f"Pest detected ({pest_name}): Monitor foliage regularly, employ physical barriers or sticky traps, and scout for population increases.",
                    "General Integrated Pest Management Principles",
                )

    # 3. Severity-Based Recommendations
    sev_level = None
    if isinstance(severity, dict):
        sev_level = severity.get("level") or severity.get("severity")

    if sev_level == "High":
        _add_rec(
            "Severe Symptom Response",
            "High severity observed: Quarantine or isolate severely damaged plants to arrest further transmission across the plot.",
            "FAO Crop Protection Guidelines",
        )
        _add_rec(
            "Expert Consultation",
            "Consult a licensed local agricultural extension agent or plant pathologist to evaluate rescue options and prevent crop failure.",
            "National Agricultural Extension Service",
        )
    elif sev_level == "Moderate":
        _add_rec(
            "Targeted Intervention",
            "Moderate symptoms observed: Prune lower infected canopy leaves and inspect adjacent plants for early lesion development.",
            "University Agricultural Extension IPM Guidelines",
        )

    # 4. Weather / Environmental Context Recommendations
    if weather and isinstance(weather, dict) and weather.get("weather_available"):
        humidity = weather.get("humidity_pct")
        if humidity is not None and humidity >= 80:
            _add_rec(
                "Humidity Management",
                f"Elevated humidity ({humidity}%): Increase ventilation in covered structures and avoid working in wet foliage to minimize spore transmission.",
                "University Agricultural Extension IPM Guidelines",
            )

        rainfall = weather.get("rainfall_mm")
        if rainfall is not None and rainfall > 2.0:
            _add_rec(
                "Rainfall Precaution",
                f"Recent rainfall ({rainfall} mm): Check for standing water around root zones and inspect for soil-splash contamination on lower leaves.",
                "Standard Agricultural Good Practices",
            )

        temp = weather.get("temperature_c")
        if temp is not None and temp >= 33:
            _add_rec(
                "Thermal Stress",
                f"High temperature ({temp}°C): Ensure adequate soil moisture and consider shade netting to mitigate heat stress and blossom drop.",
                "Standard Agricultural Good Practices",
            )

    # 5. Risk-Level-Based Urgency Guidance
    if risk_level in ("High", "Critical"):
        _add_rec(
            "Urgent Action",
            "Elevated crop health risk: Prioritize immediate scouting, restrict field traffic from infected to clean areas, and seek qualified professional agronomic advice.",
            "National Agricultural Extension Service",
        )

    # 6. Fallback if no specific recommendations generated
    if not recs:
        _add_rec(
            "General Crop Care",
            "Maintain routine field scouting, ensure balanced irrigation and soil nutrition, and consult local extension services if symptoms emerge.",
            "Standard Agricultural Good Practices",
        )

    # Final universal advisory disclaimer
    _add_rec(
        "Disclaimer",
        "NOTICE: Recommendations are general informational guidance based on integrated pest management principles. Always consult local certified agronomists and adhere to regional regulations before applying treatments.",
    )

    return recs
