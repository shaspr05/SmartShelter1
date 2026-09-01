# SMARTSHELTER

### Intelligent Thermal Comfort Analysis & Shelter Design Recommendation System
*Developed for DRDO Hackathon Software Demonstration*

---

## 1. Project Context & Problem Statement
Deploying tactical military shelters across extreme terrains (such as the Thar Desert or Siachen Glacier) requires precise physical parameter planning. Sub-optimal shelter configurations result in occupant fatigue, increased thermal signature, and reliance on high-wattage active HVAC systems. 

**SmartShelter** is a decisions-support platform that estimates indoor temperature and evaluates thermal comfort levels based on structural components (Roof, Wall, Ventilation, Shading, Size) under localized outdoor conditions. It diagnoses structural bottlenecks and optimizes the design to maximize comfort scores.

---

## 2. Core Thermal Model (Equation)
The system estimates the indoor temperature using the following linear equation:

$$T_{\text{indoor}} = T_{\text{outdoor}} + R_{\text{roof}} + R_{\text{wall}} + R_{\text{ventilation}} + R_{\text{shading}} + R_{\text{size}}$$

Where:
*   $T_{\text{outdoor}}$: Outdoor Temperature (°C)
*   $R_{\text{roof}}$: Contribution of Roof Material (°C)
*   $R_{\text{wall}}$: Contribution of Wall Material (°C)
*   $R_{\text{ventilation}}$: Ventilation relief factor (°C)
*   $R_{\text{shading}}$: Solar shielding relief factor (°C)
*   $R_{\text{size}}$: Volumetric surface ratio contribution (°C)

> [!NOTE]
> These values represent **Prototype thermal model coefficients** configured inside `data/shelter_coefficients.json` for demonstration. They should be calibrated using physical sensor feeds in real-world deployment.

---

## 3. Comfort Scoring & Humidity Engine
1.  **Trapezoidal Temperature Comfort Curve:**
    *   Target zone: $22^\circ\text{C}$ to $26^\circ\text{C}$ $\rightarrow 100\%$ Comfort.
    *   For $T_{\text{indoor}} > 26^\circ\text{C}$: comfort drops by $5\%$ per degree.
    *   For $T_{\text{indoor}} < 22^\circ\text{C}$: comfort drops by $5\%$ per degree.
2.  **Humidity Penalty:** 
    If $T_{\text{indoor}} > 26^\circ\text{C}$ and relative humidity $> 55\%$:
    $$\text{Penalty} = -\min\left(35\%, \frac{\text{Humidity} - 55}{45} \times (T_{\text{indoor}} - 26) \times 4\right)$$
3.  **Hazard Classification:**
    *   **80% – 100%:** `COMFORTABLE`
    *   **60% – 79%:** `MODERATE`
    *   **40% – 59%:** `UNCOMFORTABLE`
    *   **0% – 39%:** `CRITICAL`

---

## 4. System Architecture
```
SmartShelter/
├── app.py                      # Main Streamlit dashboard application
├── requirements.txt            # Python dependencies
├── README.md                   # Complete documentation
├── test_app.py                 # Automated unit tests
├── data/
│   ├── shelter_coefficients.json # Central configuration coefficients
│   └── simulations.csv         # Saved simulation logs
├── models/
│   ├── thermal_model.py        # Core T_indoor equation
│   ├── comfort_model.py        # Thermal comfort engine with humidity penalty
│   └── optimization_model.py   # Permutations grid search optimizer
├── engine/
│   ├── recommendation_engine.py # Problem diagnostics router
│   └── ml_module.py            # AI/ML calibration with Scikit-Learn
├── sensors/
│   └── sensor_interface.py     # Hardware telemetry providers
└── utils/
    └── helpers.py              # CSV simulation logging utilities
```

---

## 5. Setup & Installation

### Prerequisites
*   Python 3.8 to 3.12 installed on your system.

### Install Dependencies
Navigate to the root directory and install dependencies:
```bash
pip install -r requirements.txt
```

### Run Unit Tests
Verify model calculations before starting:
```bash
python test_app.py
```

### Launch the Application
Run the Streamlit server:
```bash
streamlit run app.py
```

### Public / 24x7 Hosting
This app is configured for continuous public hosting as a Streamlit web service.

Recommended options:
- Render (ready-made config in `render.yaml`)
- Docker deployment with the included `Dockerfile`
- Any container platform exposing port `8501`

Example local production startup:
```bash
chmod +x startup.sh
PORT=8501 ./startup.sh
```

For a public deployment, ensure:
- The app listens on `0.0.0.0`
- Port `8501` is exposed
- A health check or external uptime monitor is enabled
- Logs are retained and the app restarts automatically if the process crashes

---

## 6. Demonstration Steps (Hackathon Protocol)
1.  **Select Scenario:** Use the left sidebar to load "Scenario 1: Hot Desert" (Thar).
    *   Observe low comfort status (`CRITICAL` or `UNCOMFORTABLE`).
    *   View the waterfall **Thermal Contribution Graph** showing large positive bars for Metal Roof and Metal Wall.
2.  **Inspect Recommendations:** Review the prioritised diagnostic cards recommending insulated panel upgrades.
3.  **Run Design Optimizer:** Switch to the **Design Optimizer** tab and click **EXECUTE DESIGN OPTIMIZER**.
    *   Observe side-by-side comparison cards (Current vs Optimized).
    *   View the temperature reduction chart (demonstrating significant drop).
4.  **Save Simulation:** Click **Save Simulation Run** on the core dashboard to log results to the local database, exporting the results to CSV.
5.  **Try AI Calibration:** Go to **Adaptive AI Engine** and click **Fit Predictive Models**. Observe training metrics and make inference predictions using the Random Forest regressor.
