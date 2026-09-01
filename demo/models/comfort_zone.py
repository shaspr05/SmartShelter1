from typing import Dict, Any, Tuple, List

# Centralized Theme Colors (Visual Hierarchy)
COLOR_THEME = {
    "COMFORTABLE": {"hex": "#3fb950", "bg": "rgba(46, 160, 67, 0.15)", "border": "#2ea043", "icon": "🟢"},
    "MODERATE": {"hex": "#d29922", "bg": "rgba(210, 153, 34, 0.15)", "border": "#d29922", "icon": "🟡"},
    "UNCOMFORTABLE": {"hex": "#f0883e", "bg": "rgba(240, 136, 62, 0.15)", "border": "#f0883e", "icon": "🟠"},
    "CRITICAL": {"hex": "#f85149", "bg": "rgba(248, 81, 73, 0.15)", "border": "#f85149", "icon": "🔴"}
}

# Centralized Thresholds & Interpretations
ZONE_DEFINITIONS = {
    "COMFORTABLE": {
        "range": (80, 100),
        "desc": "Thermal conditions are suitable for occupants under the current model assumptions.",
        "actions": [
            "Maintain current shelter configuration.",
            "Continue monitoring temperature and humidity.",
            "No major thermal modification required."
        ]
    },
    "MODERATE": {
        "range": (60, 79),
        "desc": "Moderate thermal discomfort may occur. Targeted shelter improvements are recommended.",
        "actions_hot": [
            "Improve ventilation airflow rate.",
            "Increase perimeter solar shading.",
            "Apply roof reflective coating."
        ],
        "actions_cold": [
            "Improve wall and window insulation.",
            "Seal drafts or close unnecessary vents.",
            "Ensure tightly sealed entryways."
        ]
    },
    "UNCOMFORTABLE": {
        "range": (40, 59),
        "desc": "Significant thermal discomfort detected. Shelter modifications should be considered.",
        "actions_hot": [
            "Upgrade to Insulated Panel roofing.",
            "Install radiant barrier or reflective roof sheets.",
            "Increase cross ventilation openings.",
            "Add awnings or external shading overhangs."
        ],
        "actions_cold": [
            "Install double-walled panels with air gaps.",
            "Reduce exposed structural surface area.",
            "Seal micro-vent openings.",
            "Install insulation on walls and flooring."
        ]
    },
    "CRITICAL": {
        "range": (0, 39),
        "desc": "Severe thermal discomfort detected. Immediate shelter design intervention is recommended.",
        "actions_hot": [
            "Enable high-efficiency cross-ventilation or extraction fans.",
            "Deploy external solar shade nets and canopy overhangs.",
            "Upgrade to Insulated Roof and Insulated Wall systems.",
            "Consider mechanical or active evaporative cooling if powered."
        ],
        "actions_cold": [
            "Maximize wall and roof insulation thickness.",
            "Minimize active ventilation to essential life-safety levels.",
            "Close all solar/wind exposure gaps completely.",
            "Deploy localized auxiliary heating systems."
        ]
    }
}

def get_comfort_zone(comfort_percentage: float) -> str:
    """Clamps comfort percentage and retrieves the corresponding zone."""
    val = max(0.0, min(100.0, comfort_percentage))
    if val >= 80.0:
        return "COMFORTABLE"
    elif val >= 60.0:
        return "MODERATE"
    elif val >= 40.0:
        return "UNCOMFORTABLE"
    else:
        return "CRITICAL"

def get_zone_description(zone: str) -> str:
    """Gets the user-facing explanation for a given comfort zone."""
    return ZONE_DEFINITIONS.get(zone, {}).get("desc", "")

def get_thermal_condition(t_indoor: float, target_low: float = 22.0, target_high: float = 26.0) -> str:
    """
    Distinguishes whether discomfort is primarily due to heat or cold based on target range.
    """
    if target_low <= t_indoor <= target_high:
        return "COMFORTABLE"
    elif t_indoor > target_high:
        return "CRITICAL_HEAT" if t_indoor >= 35.0 else "HEAT_DISCOMFORT"
    else:
        return "CRITICAL_COLD" if t_indoor <= 10.0 else "COLD_DISCOMFORT"

def get_zone_recommendations(zone: str, condition: str) -> List[str]:
    """Gets prioritized recommendations based on zone level and thermal condition."""
    defn = ZONE_DEFINITIONS.get(zone, {})
    if zone == "COMFORTABLE":
        return defn.get("actions", [])
    
    is_hot = "HEAT" in condition or condition == "COMFORTABLE"
    key = "actions_hot" if is_hot else "actions_cold"
    return defn.get(key, [])
