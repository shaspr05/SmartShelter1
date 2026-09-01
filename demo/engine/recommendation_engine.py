from typing import List, Dict, Any

class RecommendationEngine:
    """
    Analyzes shelter thermal parameters and environmental inputs to diagnose problems,
    mapping them back to comfort zones with clear physical action priorities.
    """
    def __init__(self):
        pass

    def analyze_and_recommend(
        self,
        t_outdoor: float,
        humidity: float,
        wind_speed: float,
        solar_exposure: str,
        roof: str,
        wall: str,
        ventilation: str,
        shading: str,
        t_indoor: float,
        breakdown: Dict[str, float],
        comfort_status: str
    ) -> List[Dict[str, Any]]:
        """
        Returns a list of diagnosed problems with details:
        - Problem Title
        - Evidence
        - Recommended Action
        - Priority (HIGH, MEDIUM, LOW)
        """
        recommendations = []

        # Extract coefficients/contributions
        r_roof = breakdown.get("roof", 0.0)
        r_wall = breakdown.get("wall", 0.0)
        r_vent = breakdown.get("ventilation", 0.0)
        r_shade = breakdown.get("shading", 0.0)

        is_hot = t_indoor > 26.0
        is_cold = t_indoor < 22.0

        # Don't make recommendations if completely comfortable
        if comfort_status == "COMFORTABLE":
            recommendations.append({
                "problem": "Thermal parameters are optimal",
                "evidence": f"Estimated indoor temperature of {t_indoor:.1f}°C is within the target comfort zone.",
                "action": "Maintain current shelter configuration. No major thermal modification required.",
                "priority": "LOW"
            })
            return recommendations

        if is_hot:
            # Roof insulation check
            if r_roof > 0:
                priority = "HIGH" if r_roof >= 3.0 else ("MEDIUM" if r_roof >= 1.5 else "LOW")
                action_text = "Improve roof insulation."
                if comfort_status == "CRITICAL":
                    action_text = "CRITICAL INTERVENTION: Apply high-efficiency thermal panels or reflective coating immediately."
                recommendations.append({
                    "problem": "Roof thermal contribution",
                    "evidence": f"Roof component adds +{r_roof:.1f}°C to thermal load.",
                    "action": action_text,
                    "priority": priority
                })

            # Wall insulation check
            if r_wall > 0:
                priority = "HIGH" if r_wall >= 3.0 else ("MEDIUM" if r_wall >= 1.5 else "LOW")
                action_text = "Improve wall insulation."
                recommendations.append({
                    "problem": "Wall thermal contribution",
                    "evidence": f"Wall structure adds +{r_wall:.1f}°C to internal temperature.",
                    "action": action_text,
                    "priority": priority
                })

            # Shading check
            if shading in ["None", "Low"]:
                priority = "HIGH" if solar_exposure in ["High", "Extreme"] else "MEDIUM"
                recommendations.append({
                    "problem": "Solar heat gain due to weak shading",
                    "evidence": f"Solar exposure is '{solar_exposure}' with minimal shading relief ({r_shade:.1f}°C).",
                    "action": "Deploy external shading sheets, mesh sails, or extend the roof overhang.",
                    "priority": priority
                })

            # Ventilation check
            if ventilation in ["Poor", "Moderate"]:
                priority = "HIGH" if comfort_status == "CRITICAL" else "MEDIUM"
                recommendations.append({
                    "problem": "Air accumulation and low ventilation",
                    "evidence": f"Ventilation is '{ventilation}' limiting negative heat relief to {r_vent:.1f}°C.",
                    "action": "Increase active cross ventilation or configure mechanical exhaust pathways.",
                    "priority": priority
                })


        elif is_cold:
            # Cold environment check: positive coefficients are good (retaining heat), negative ones (ventilation/shading cooling) need restriction
            # Roof heat loss check
            if roof in ["Metal", "Fabric"] or r_roof > 2.0:
                recommendations.append({
                    "problem": "Roof envelope heat leakage",
                    "evidence": f"Roof selection '{roof}' is thin and allows heat to escape.",
                    "action": "Upgrade to Insulated Roof Panels to trap warmth.",
                    "priority": "HIGH"
                })

            # Wall heat loss check
            if wall in ["Metal", "Fabric"] or r_wall > 1.5:
                recommendations.append({
                    "problem": "Wall thermal transmittance",
                    "evidence": f"Wall material '{wall}' has high thermal leakage.",
                    "action": "Upgrade to composite/insulated panels or double wall configurations.",
                    "priority": "HIGH"
                })

            # Ventilation cooling check
            if ventilation in ["Excellent", "Good"]:
                priority = "HIGH" if comfort_status == "CRITICAL" else "MEDIUM"
                recommendations.append({
                    "problem": "Excessive cold air draft ventilation",
                    "evidence": f"Air exchange is '{ventilation}' adding {r_vent:.1f}°C of cooling draft.",
                    "action": "Restrict ventilation openings, seal leaks, and consider vestibule entries.",
                    "priority": priority
                })

            # Shading cooling check
            if shading in ["High", "External Shading"]:
                recommendations.append({
                    "problem": "Solar heat blockage under cold conditions",
                    "evidence": f"External shading blocks solar gain and contributes {r_shade:.1f}°C of cooling.",
                    "action": "Remove shading elements to allow solar heat to warm the shelter envelope during daytime.",
                    "priority": "LOW"
                })

        # Add critical intervention tag if status is critical
        if comfort_status == "CRITICAL":
            recommendations.append({
                "problem": "Critical thermal hazard alert",
                "evidence": "Model estimates extreme temperature zone.",
                "action": "Immediate envelope overhaul required to protect occupants from severe thermal strain.",
                "priority": "HIGH"
            })

        # Sort recommendations: HIGH -> MEDIUM -> LOW
        priority_map = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        recommendations.sort(key=lambda x: priority_map.get(x["priority"], 3))

        return recommendations
