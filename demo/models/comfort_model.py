from typing import Tuple, Dict, Any

class ComfortModel:
    """
    Thermal Comfort Engine that evaluates comfort scores and applies relative humidity penalties.
    """
    def __init__(self, target_low: float = 22.0, target_high: float = 26.0):
        self.target_low = target_low
        self.target_high = target_high

    def calculate_comfort(self, t_indoor: float, humidity: float) -> Tuple[float, float, float, str]:
        """
        Calculates comfort metrics.
        
        Returns:
            Tuple of:
              - temperature comfort score (float, 0-100)
              - humidity adjustment penalty (float, <= 0)
              - final comfort score (float, 0-100)
              - comfort status (str: COMFORTABLE, MODERATE, UNCOMFORTABLE, CRITICAL)
        """
        # 1. Base Temperature Comfort Score (Trapezoidal model)
        if self.target_low <= t_indoor <= self.target_high:
            temp_score = 100.0
        elif t_indoor > self.target_high:
            # Drop score as it gets hotter (reaches 0% around 46°C)
            temp_score = max(0.0, 100.0 - (t_indoor - self.target_high) * 5.0)
        else:
            # Drop score as it gets colder (reaches 0% around 2°C)
            temp_score = max(0.0, 100.0 - (self.target_low - t_indoor) * 5.0)

        # 2. Humidity Penalty (only under high temperatures, e.g. T > 26°C)
        humidity_penalty = 0.0
        if t_indoor > 26.0 and humidity > 55.0:
            # Scaled penalty based on how far humidity is above 55% and temperature above 26C
            humidity_factor = (humidity - 55.0) / 45.0  # Normalized 0 to 1 for 55% to 100%
            temp_excess = t_indoor - 26.0
            humidity_penalty = -1.0 * min(35.0, humidity_factor * temp_excess * 4.0)

        # 3. Final Comfort Score
        final_score = max(0.0, min(100.0, temp_score + humidity_penalty))

        # Round figures for display
        temp_score = round(temp_score, 1)
        humidity_penalty = round(humidity_penalty, 1)
        final_score = round(final_score, 1)

        # 4. Classification
        from models.comfort_zone import get_comfort_zone
        status = get_comfort_zone(final_score)

        return temp_score, humidity_penalty, final_score, status
