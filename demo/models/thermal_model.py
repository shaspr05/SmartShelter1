import os
import json
from typing import Dict, Any, Tuple

# Fallback values if configuration file is missing
DEFAULT_COEFFICIENTS = {
    "roof": {
        "Metal": 4.5,
        "Reflective Metal": 1.5,
        "Concrete": 3.0,
        "Insulated Panel": 0.5,
        "Fabric": 4.0,
        "Composite": 2.0,
        "Custom": 2.5
    },
    "wall": {
        "Metal": 3.0,
        "Concrete": 2.0,
        "Brick": 1.5,
        "Insulated Panel": 0.2,
        "Fabric": 3.5,
        "Composite": 1.0,
        "Custom": 1.5
    },
    "ventilation": {
        "Poor": 0.0,
        "Moderate": -1.5,
        "Good": -3.0,
        "Excellent": -4.5
    },
    "shading": {
        "None": 0.0,
        "Low": -1.0,
        "Medium": -2.5,
        "High": -4.0,
        "External Shading": -5.0
    },
    "size": {
        "Small (2-4 Pax)": 1.0,
        "Medium (6-8 Pax)": 0.0,
        "Large (10-12 Pax)": -1.0
    }
}

class ThermalModel:
    """
    Thermal Model implementing the prototype indoor temperature equation:
    T_indoor = T_outdoor + R_roof + R_wall + R_ventilation + R_shading
    """
    def __init__(self, coeff_path: str = "data/shelter_coefficients.json"):
        self.coeff_path = coeff_path
        self.coefficients = self._load_coefficients()

    def _load_coefficients(self) -> Dict[str, Dict[str, float]]:
        """Load coefficients from JSON file or fall back to default model values."""
        if os.path.exists(self.coeff_path):
            try:
                with open(self.coeff_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading {self.coeff_path}: {e}. Using defaults.")
        return DEFAULT_COEFFICIENTS

    def calculate_indoor_temperature(
        self,
        t_outdoor: float,
        roof_material: str,
        wall_material: str,
        ventilation_level: str,
        shading_level: str,
        shelter_size: str = "Medium (6-8 Pax)"
    ) -> Tuple[float, Dict[str, float]]:
        """
        Estimates the indoor temperature based on outdoor conditions and shelter components.
        
        Returns:
            Tuple of:
              - calculated indoor temperature (float)
              - contribution breakdown dictionary (Dict[str, float])
        """
        # Look up values with fallbacks to defaults
        r_roof = self.coefficients.get("roof", {}).get(roof_material, 0.0)
        r_wall = self.coefficients.get("wall", {}).get(wall_material, 0.0)
        r_vent = self.coefficients.get("ventilation", {}).get(ventilation_level, 0.0)
        r_shade = self.coefficients.get("shading", {}).get(shading_level, 0.0)
        r_size = self.coefficients.get("size", {}).get(shelter_size, 0.0)

        # Formula: T_indoor = T_outdoor + Roof + Wall + Vent + Shade + Size
        t_indoor = t_outdoor + r_roof + r_wall + r_vent + r_shade + r_size

        breakdown = {
            "outdoor": t_outdoor,
            "roof": r_roof,
            "wall": r_wall,
            "ventilation": r_vent,
            "shading": r_shade,
            "size": r_size,
        }

        return round(t_indoor, 2), breakdown
