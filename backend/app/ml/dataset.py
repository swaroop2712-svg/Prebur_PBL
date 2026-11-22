"""Synthetic / Demo Dataset Generator for PreBurn Stubble Burning ML Model.

Features:
- Temperature (°C)
- Humidity (%)
- Wind speed (km/h)
- Rainfall (mm)
- Crop maturity (%)
- Sowing-deadline pressure (0-100 index)
- Historical burning data (district fire intensity index 0-100)

Target:
- burning_event (0 or 1)
"""

import os
import random
import csv

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATASET_PATH = os.path.join(DATA_DIR, "synthetic_stubble_burning_training_data.csv")

FEATURE_NAMES = [
    "temperature",
    "humidity",
    "wind_speed",
    "rainfall",
    "crop_maturity",
    "sowing_deadline_pressure",
    "historical_burning_data"
]


def generate_synthetic_dataset(num_samples: int = 1500, seed: int = 42) -> str:
    """Generate a realistic synthetic training dataset for northern India stubble burning season.
    
    Generates realistic correlation between weather, harvest timeline, wheat sowing pressure,
    historical burning patterns, and actual burning events.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    random.seed(seed)

    rows = []
    for _ in range(num_samples):
        # Weather features (Oct-Nov North India post-monsoon conditions)
        temp = round(random.uniform(20.0, 36.0), 1)
        humidity = round(random.uniform(25.0, 85.0), 1)
        wind = round(random.uniform(3.0, 24.0), 1)
        # Most days have 0 rainfall; occasional showers
        rainfall = round(random.choices([0.0, random.uniform(0.1, 4.0), random.uniform(5.0, 30.0)], weights=[0.82, 0.12, 0.06])[0], 1)

        # Agronomic and operational pressure features
        crop_maturity = round(random.uniform(30.0, 100.0), 1)
        sowing_pressure = round(random.uniform(15.0, 100.0), 1)
        historical_burning = round(random.uniform(10.0, 95.0), 1)

        # Realistic burning probability score:
        # High crop maturity + high sowing pressure + low humidity + high temp + high historical rate => High probability
        score = 0.0
        score += (crop_maturity / 100.0) * 0.28
        score += (sowing_pressure / 100.0) * 0.30
        score += (historical_burning / 100.0) * 0.20
        score += ((temp - 20.0) / 16.0) * 0.10
        score += ((85.0 - humidity) / 60.0) * 0.08
        score += ((wind - 3.0) / 21.0) * 0.04

        # Rainfall heavily dampens burning
        if rainfall > 2.0:
            score *= 0.15
        elif rainfall > 0.0:
            score *= 0.60

        # Add slight natural variance
        score += random.gauss(0, 0.05)
        score = max(0.0, min(1.0, score))

        # Binary label: 1 if burning occurred, 0 otherwise (threshold ~ 0.52)
        burning_event = 1 if score >= 0.52 else 0

        rows.append([
            temp,
            humidity,
            wind,
            rainfall,
            crop_maturity,
            sowing_pressure,
            historical_burning,
            burning_event
        ])

    with open(DATASET_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(FEATURE_NAMES + ["burning_event"])
        writer.writerows(rows)

    return DATASET_PATH


if __name__ == "__main__":
    path = generate_synthetic_dataset()
    print(f"Dataset generated at {path}")
