import os
import csv
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

SIMULATIONS_PATH = "data/simulations.csv"

def init_simulation_log():
    """Initializes the simulation CSV file with columns if it doesn't exist."""
    os.makedirs(os.path.dirname(SIMULATIONS_PATH), exist_ok=True)
    if not os.path.exists(SIMULATIONS_PATH):
        headers = [
            "Timestamp", "Outdoor Temp (°C)", "Humidity (%)", "Wind Speed (m/s)", "Solar Exposure",
            "Roof", "Wall", "Ventilation", "Shading", "Size", "Indoor Temp (°C)", "Comfort Score (%)", "Status", "Primary Condition"
        ]
        with open(SIMULATIONS_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

def log_simulation(
    t_outdoor: float,
    humidity: float,
    wind_speed: float,
    solar_exposure: str,
    roof: str,
    wall: str,
    ventilation: str,
    shading: str,
    size: str,
    t_indoor: float,
    comfort_score: float,
    status: str,
    primary_condition: str
):
    """Appends a new simulation run to the CSV log."""
    init_simulation_log()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        timestamp, t_outdoor, humidity, wind_speed, solar_exposure,
        roof, wall, ventilation, shading, size, t_indoor, comfort_score, status, primary_condition
    ]
    with open(SIMULATIONS_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

def load_simulations() -> pd.DataFrame:
    """Loads previous simulation records from CSV."""
    init_simulation_log()
    try:
        for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
            try:
                df = pd.read_csv(SIMULATIONS_PATH, encoding=encoding)
                return df
            except UnicodeDecodeError:
                continue
        return pd.read_csv(SIMULATIONS_PATH, engine="python", encoding_errors="replace")
    except Exception as e:
        print(f"Error loading simulations: {e}")
        return pd.DataFrame()

def clear_simulations():
    """Removes all saved simulations by deleting and re-creating the CSV file."""
    if os.path.exists(SIMULATIONS_PATH):
        os.remove(SIMULATIONS_PATH)
    init_simulation_log()
