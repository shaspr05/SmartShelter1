from typing import Dict, Any, List, Tuple
from models.thermal_model import ThermalModel
from models.comfort_model import ComfortModel

class OptimizationModel:
    """
    Evaluates all shelter component combinations to select and rank
    the optimal setup for thermal comfort under current environmental parameters.
    """
    def __init__(self, thermal_model: ThermalModel, comfort_model: ComfortModel):
        self.thermal_model = thermal_model
        self.comfort_model = comfort_model

    def optimize(
        self,
        t_outdoor: float,
        humidity: float,
        solar_exposure: str,
        current_config: Dict[str, str]
    ) -> Tuple[Dict[str, Any], Dict[str, Any], float, float]:
        """
        Runs a grid search over all combinations of roof, wall, ventilation, and shading.
        Keep size constant (as size is typically determined by capacity needs).
        
        Returns:
            Tuple of:
              - Best configuration dictionary with calculations
              - Current configuration dictionary with calculations
              - Temperature reduction/difference (float)
              - Comfort score improvement points (float)
        """
        roof_options = list(self.thermal_model.coefficients.get("roof", {}).keys())
        wall_options = list(self.thermal_model.coefficients.get("wall", {}).keys())
        vent_options = list(self.thermal_model.coefficients.get("ventilation", {}).keys())
        shade_options = list(self.thermal_model.coefficients.get("shading", {}).keys())

        # Map comfort status to integer priority weights
        status_weights = {
            "COMFORTABLE": 4,
            "MODERATE": 3,
            "UNCOMFORTABLE": 2,
            "CRITICAL": 1
        }

        size = current_config.get("size", "Medium (6-8 Pax)")

        best_rank = (-1, -1.0, -999.0)
        best_cfg = None

        # Grid search
        for r in roof_options:
            for w in wall_options:
                for v in vent_options:
                    for s in shade_options:
                        # Calculate thermal impact
                        t_ind, breakdown = self.thermal_model.calculate_indoor_temperature(
                            t_outdoor=t_outdoor,
                            roof_material=r,
                            wall_material=w,
                            ventilation_level=v,
                            shading_level=s,
                            shelter_size=size
                        )
                        # Calculate comfort score
                        _, _, comfort_score, status = self.comfort_model.calculate_comfort(
                            t_indoor=t_ind,
                            humidity=humidity
                        )
                        
                        # Rank criteria: (Zone weight, Comfort percentage, -Distance to 24.0C)
                        curr_weight = status_weights.get(status, 0)
                        curr_dist = abs(t_ind - 24.0)
                        curr_rank = (curr_weight, comfort_score, -curr_dist)

                        if curr_rank > best_rank:
                            best_rank = curr_rank
                            best_cfg = {
                                "roof": r,
                                "wall": w,
                                "ventilation": v,
                                "shading": s,
                                "size": size,
                                "t_indoor": t_ind,
                                "comfort_score": comfort_score,
                                "comfort_status": status,
                                "breakdown": breakdown
                            }

        # Get current config values
        curr_t_ind, curr_breakdown = self.thermal_model.calculate_indoor_temperature(
            t_outdoor=t_outdoor,
            roof_material=current_config.get("roof"),
            wall_material=current_config.get("wall"),
            ventilation_level=current_config.get("ventilation"),
            shading_level=current_config.get("shading"),
            shelter_size=size
        )
        _, _, curr_comfort, curr_status = self.comfort_model.calculate_comfort(
            t_indoor=curr_t_ind,
            humidity=humidity
        )
        
        current_cfg_stats = {
            "roof": current_config.get("roof"),
            "wall": current_config.get("wall"),
            "ventilation": current_config.get("ventilation"),
            "shading": current_config.get("shading"),
            "size": size,
            "t_indoor": curr_t_ind,
            "comfort_score": curr_comfort,
            "comfort_status": curr_status,
            "breakdown": curr_breakdown
        }

        temp_diff = curr_t_ind - best_cfg["t_indoor"]
        comfort_diff = best_cfg["comfort_score"] - curr_comfort

        return best_cfg, current_cfg_stats, round(temp_diff, 2), round(comfort_diff, 2)
