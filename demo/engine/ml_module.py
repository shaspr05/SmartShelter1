import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

class SmartShelterML:
    """
    Optional AI/ML module for coefficient calibration and comfort predictions.
    Leverages experimental field observations to improve the engineering formulas.
    """
    def __init__(self):
        self.temp_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.calibrator = LinearRegression()
        self.is_trained = False

    def generate_mock_experimental_data(self, size: int = 500) -> pd.DataFrame:
        """
        Generates simulated real-world sensor logs for model training.
        """
        np.random.seed(42)
        
        # Draw random values
        t_out = np.random.uniform(15.0, 45.0, size)
        humidity = np.random.uniform(30.0, 95.0, size)
        
        # Random categorical variables mapped to integers
        roof_idx = np.random.randint(0, 3, size)
        wall_idx = np.random.randint(0, 3, size)
        vent_idx = np.random.randint(0, 3, size)
        
        # Simulated actual measured indoor temperature with noise
        # Base: t_indoor = t_outdoor + coefficients + physical noise
        t_in = t_out + (roof_idx * 1.5) + (wall_idx * 1.0) - (vent_idx * 1.2) + np.random.normal(0.0, 0.8, size)
        
        df = pd.DataFrame({
            "t_outdoor": t_out,
            "humidity": humidity,
            "roof_code": roof_idx,
            "wall_code": wall_idx,
            "vent_code": vent_idx,
            "t_indoor_observed": t_in
        })
        return df

    def train_predictive_comfort(self) -> Dict[str, Any]:
        """
        Trains a RandomForestRegressor to predict observed indoor temperature from
        environmental features and shelter codes.
        """
        df = self.generate_mock_experimental_data()
        X = df[["t_outdoor", "humidity", "roof_code", "wall_code", "vent_code"]]
        y = df["t_indoor_observed"]
        
        self.temp_model.fit(X, y)
        self.is_trained = True
        
        # Calculate R2 score on training data for presentation metrics
        r2_score = self.temp_model.score(X, y)
        
        return {
            "model_type": "RandomForestRegressor",
            "samples_trained": len(df),
            "r2_score": round(r2_score, 4),
            "features_used": list(X.columns)
        }

    def calibrate_coefficients(self) -> Dict[str, Dict[str, float]]:
        """
        Performs calibration of selected coefficients (e.g. Metal vs Concrete) using
        a Linear Regression model mapping dummy categories back to delta (T_indoor - T_outdoor).
        """
        df = self.generate_mock_experimental_data(size=200)
        
        # Delta T is the target for contribution coefficients
        y = df["t_indoor_observed"] - df["t_outdoor"]
        
        # Create features for Roof: index 0 (Metal), 1 (Reflective), 2 (Insulated)
        X_roof_1 = (df["roof_code"] == 1).astype(float)
        X_roof_2 = (df["roof_code"] == 2).astype(float)
        
        X = pd.DataFrame({
            "Reflective_Metal_Delta": X_roof_1,
            "Insulated_Panel_Delta": X_roof_2
        })
        
        self.calibrator.fit(X, y)
        
        # Calculate calibrated values (base intercept represents 'Metal')
        metal_calib = float(self.calibrator.intercept_)
        reflective_calib = metal_calib + float(self.calibrator.coef_[0])
        insulated_calib = metal_calib + float(self.calibrator.coef_[1])
        
        return {
            "calibrated_roof_coefficients": {
                "Metal (Calibrated)": round(metal_calib, 2),
                "Reflective Metal (Calibrated)": round(reflective_calib, 2),
                "Insulated Panel (Calibrated)": round(insulated_calib, 2)
            }
        }
