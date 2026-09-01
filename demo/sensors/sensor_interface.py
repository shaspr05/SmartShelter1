import time
import random
from typing import Dict, Any

class SensorProvider:
    """
    Base class outlining the contract for environmental data feeds.
    Allows transparent transition from manual forms to API/hardware feeds.
    """
    def read_data(self) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement read_data")

class ManualSensorProvider(SensorProvider):
    """
    Provides environmental data manually inputted by the dashboard user.
    """
    def __init__(self, t_outdoor: float, humidity: float, wind_speed: float, solar_exposure: str):
        self.t_outdoor = t_outdoor
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.solar_exposure = solar_exposure

    def read_data(self) -> Dict[str, Any]:
        return {
            "outdoor_temperature": self.t_outdoor,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "solar_exposure": self.solar_exposure,
            "timestamp": time.time(),
            "provider": "Manual Input"
        }

class MockIoTSensorProvider(SensorProvider):
    """
    Mock IoT sensor provider representing an ESP32 or Arduino sending serial/MQTT data.
    Provides synthetic values with random fluctuation around a baseline.
    """
    def __init__(self, base_temp: float = 38.0, base_humidity: float = 65.0):
        self.base_temp = base_temp
        self.base_humidity = base_humidity

    def read_data(self) -> Dict[str, Any]:
        # Introduce tiny random fluctuations to simulate live sensors
        t_fluct = round(self.base_temp + random.uniform(-0.5, 0.5), 1)
        h_fluct = round(self.base_humidity + random.uniform(-2.0, 2.0), 1)
        # Cap humidity at 100%
        h_fluct = max(0.0, min(100.0, h_fluct))
        
        return {
            "outdoor_temperature": t_fluct,
            "humidity": h_fluct,
            "wind_speed": round(random.uniform(1.0, 8.0), 1),
            "solar_exposure": random.choice(["Medium", "High", "Extreme"]),
            "timestamp": time.time(),
            "provider": "IoT ESP32 Mock Server (MQTT/TCP)"
        }
