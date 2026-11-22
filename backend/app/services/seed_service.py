import logging
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from app.models import (
    State,
    District,
    RiskPrediction,
    FireDetection,
    WeatherForecast,
    Alert
)
from app.utils.helpers import calculate_risk_level

logger = logging.getLogger("preburn.seed")

PUNJAB_DISTRICTS = [
    {"name": "Ludhiana", "lat": 30.9010, "lon": 75.8573, "base_prob": 87.0},
    {"name": "Patiala", "lat": 30.3398, "lon": 76.3869, "base_prob": 76.0},
    {"name": "Amritsar", "lat": 31.6340, "lon": 74.8723, "base_prob": 62.0},
    {"name": "Sangrur", "lat": 30.2458, "lon": 75.8421, "base_prob": 58.0},
    {"name": "Bathinda", "lat": 30.2110, "lon": 74.9455, "base_prob": 48.0},
    {"name": "Jalandhar", "lat": 31.3260, "lon": 75.5762, "base_prob": 66.0},
    {"name": "Kapurthala", "lat": 31.3800, "lon": 75.3800, "base_prob": 35.0},
    {"name": "Fazilka", "lat": 30.4036, "lon": 74.0270, "base_prob": 38.0},
    {"name": "Gurdaspur", "lat": 32.0419, "lon": 75.4053, "base_prob": 52.0},
    {"name": "Firozpur", "lat": 30.9237, "lon": 74.6122, "base_prob": 68.0},
    {"name": "Mansa", "lat": 29.9880, "lon": 75.3920, "base_prob": 55.0},
    {"name": "Barnala", "lat": 30.3819, "lon": 75.5466, "base_prob": 59.0},
    {"name": "Faridkot", "lat": 30.6769, "lon": 74.7583, "base_prob": 61.0},
    {"name": "Tarn Taran", "lat": 31.4520, "lon": 74.9250, "base_prob": 70.0},
    {"name": "Moga", "lat": 30.8165, "lon": 75.1717, "base_prob": 64.0},
    {"name": "Muktsar", "lat": 30.4744, "lon": 74.5165, "base_prob": 53.0},
    {"name": "Hoshiarpur", "lat": 31.5273, "lon": 75.9149, "base_prob": 31.0},
    {"name": "Rupnagar", "lat": 30.9664, "lon": 76.5331, "base_prob": 26.0},
    {"name": "Fatehgarh Sahib", "lat": 30.6480, "lon": 76.3980, "base_prob": 44.0},
    {"name": "SAS Nagar (Mohali)", "lat": 30.7046, "lon": 76.7179, "base_prob": 28.0},
    {"name": "Nawanshahr", "lat": 31.1256, "lon": 76.1189, "base_prob": 34.0},
    {"name": "Pathankot", "lat": 32.2688, "lon": 75.6499, "base_prob": 22.0},
]

HARYANA_DISTRICTS = [
    {"name": "Karnal", "lat": 29.6857, "lon": 76.9905, "base_prob": 54.0},
    {"name": "Hisar", "lat": 29.1492, "lon": 75.7217, "base_prob": 32.0},
    {"name": "Panipat", "lat": 29.3909, "lon": 76.9635, "base_prob": 29.0},
    {"name": "Rohtak", "lat": 28.8955, "lon": 76.6066, "base_prob": 37.0},
    {"name": "Sirsa", "lat": 29.5349, "lon": 75.0296, "base_prob": 49.0},
    {"name": "Kurukshetra", "lat": 29.9695, "lon": 76.8783, "base_prob": 56.0},
    {"name": "Ambala", "lat": 30.3782, "lon": 76.7767, "base_prob": 42.0},
    {"name": "Fatehabad", "lat": 29.5152, "lon": 75.4510, "base_prob": 51.0},
    {"name": "Jind", "lat": 29.3160, "lon": 76.3150, "base_prob": 46.0},
    {"name": "Kaithal", "lat": 29.8015, "lon": 76.3996, "base_prob": 58.0},
    {"name": "Sonipat", "lat": 28.9931, "lon": 77.0151, "base_prob": 33.0},
    {"name": "Yamunanagar", "lat": 30.1290, "lon": 77.2674, "base_prob": 25.0},
    {"name": "Bhiwani", "lat": 28.7831, "lon": 76.1397, "base_prob": 24.0},
    {"name": "Jhajjar", "lat": 28.6063, "lon": 76.6565, "base_prob": 27.0},
    {"name": "Gurugram", "lat": 28.4595, "lon": 77.0266, "base_prob": 18.0},
    {"name": "Faridabad", "lat": 28.4089, "lon": 77.3178, "base_prob": 15.0},
]


def seed_initial_data(db: Session):
    """Seed states, districts, fire detections, weather, predictions and alerts."""
    # Check if already seeded
    if db.query(State).count() > 0:
        logger.info("Database already seeded. Skipping initial seeding.")
        return

    logger.info("Starting database seeding...")

    # 1. Seed States
    punjab = State(name="Punjab", code="PB")
    haryana = State(name="Haryana", code="HR")
    db.add_all([punjab, haryana])
    db.flush()

    # 2. Seed Districts
    district_map = {}
    district_base_probs = {}

    for d in PUNJAB_DISTRICTS:
        dist = District(
            state_id=punjab.id,
            name=d["name"],
            latitude=d["lat"],
            longitude=d["lon"]
        )
        db.add(dist)
        db.flush()
        district_map[d["name"]] = dist
        district_base_probs[dist.id] = d["base_prob"]

    for d in HARYANA_DISTRICTS:
        dist = District(
            state_id=haryana.id,
            name=d["name"],
            latitude=d["lat"],
            longitude=d["lon"]
        )
        db.add(dist)
        db.flush()
        district_map[d["name"]] = dist
        district_base_probs[dist.id] = d["base_prob"]

    today = date(2025, 10, 15)

    # 3. Seed Fire Detections (matching and expanding prototype)
    fires_data = [
        ("2025-10-15", "Ludhiana", 30.9010, 75.8573, "VIIRS SNPP", "High", 12.4),
        ("2025-10-15", "Patiala", 30.3398, 76.3869, "VIIRS NOAA-20", "Nominal", 8.7),
        ("2025-10-14", "Sangrur", 30.2458, 75.8421, "VIIRS SNPP", "High", 10.2),
        ("2025-10-14", "Karnal", 29.6857, 76.9905, "VIIRS NOAA-20", "Nominal", 6.8),
        ("2025-10-13", "Hisar", 29.1492, 75.7217, "VIIRS SNPP", "Nominal", 4.2),
        ("2025-10-13", "Amritsar", 31.6340, 74.8723, "VIIRS NOAA-20", "High", 7.1),
        ("2025-10-12", "Panipat", 29.3909, 76.9635, "VIIRS SNPP", "Nominal", 5.4),
        ("2025-10-12", "Bathinda", 30.2110, 74.9455, "VIIRS SNPP", "High", 8.9),
        ("2025-10-11", "Tarn Taran", 31.4520, 74.9250, "VIIRS NOAA-20", "High", 11.5),
        ("2025-10-11", "Kaithal", 29.8015, 76.3996, "VIIRS SNPP", "Nominal", 6.1),
        ("2025-10-10", "Firozpur", 30.9237, 74.6122, "VIIRS SNPP", "High", 9.4),
        ("2025-10-09", "Kurukshetra", 29.9695, 76.8783, "VIIRS NOAA-20", "Nominal", 4.8),
    ]

    for f in fires_data:
        d_name = f[1]
        dist = district_map.get(d_name)
        db.add(FireDetection(
            district_id=dist.id if dist else None,
            detection_date=datetime.strptime(f[0], "%Y-%m-%d").date(),
            latitude=f[2],
            longitude=f[3],
            satellite=f[4],
            confidence=f[5],
            frp=f[6]
        ))

    # 4. Seed Weather Forecasts (4 days per district)
    weather_templates = {
        "Ludhiana": [
            {"temp": 32.0, "hum": 48.0, "wind": 12.0, "cond": "Sunny"},
            {"temp": 31.0, "hum": 55.0, "wind": 10.0, "cond": "Sunny"},
            {"temp": 29.0, "hum": 62.0, "wind": 8.0, "cond": "Partly Cloudy"},
            {"temp": 27.0, "hum": 69.0, "wind": 6.0, "cond": "Rain"}
        ],
        "Karnal": [
            {"temp": 31.0, "hum": 46.0, "wind": 11.0, "cond": "Sunny"},
            {"temp": 30.0, "hum": 52.0, "wind": 9.0, "cond": "Sunny"},
            {"temp": 28.0, "hum": 58.0, "wind": 8.0, "cond": "Partly Cloudy"},
            {"temp": 27.0, "hum": 64.0, "wind": 7.0, "cond": "Rain"}
        ]
    }

    default_weather = [
        {"temp": 30.0, "hum": 50.0, "wind": 10.0, "cond": "Sunny"},
        {"temp": 29.0, "hum": 55.0, "wind": 9.0, "cond": "Sunny"},
        {"temp": 28.0, "hum": 60.0, "wind": 8.0, "cond": "Partly Cloudy"},
        {"temp": 26.0, "hum": 65.0, "wind": 7.0, "cond": "Rain"}
    ]

    for name, dist in district_map.items():
        template = weather_templates.get(name, default_weather)
        for i, w in enumerate(template):
            f_date = today + timedelta(days=i)
            db.add(WeatherForecast(
                district_id=dist.id,
                forecast_date=f_date,
                temperature=w["temp"],
                humidity=w["hum"],
                wind_speed=w["wind"],
                condition=w["cond"]
            ))

    # 5. Seed Risk Predictions (3-day default horizon for all districts)
    for dist_id, prob in district_base_probs.items():
        level = calculate_risk_level(prob)
        db.add(RiskPrediction(
            district_id=dist_id,
            prediction_date=today,
            horizon_days=3,
            probability=prob,
            risk_level=level
        ))

    # 6. Seed Alerts
    alerts_data = [
        ("High risk detected in Ludhiana (Punjab)",
         "High probability of stubble burning (87%) predicted within next 3 days. Elevated thermal activity expected.",
         "High", "Ludhiana", False, datetime(2025, 10, 15, 8, 42)),
        ("Fire location detected near Sangrur (Punjab)",
         "Satellite VIIRS SNPP detected active fire cluster with 10.2 MW Fire Radiative Power.",
         "High", "Sangrur", False, datetime(2025, 10, 14, 18, 17)),
        ("Medium risk in Patiala (Punjab)",
         "Favorable weather conditions and post-harvest drying increase burning risk to 76%.",
         "Medium", "Patiala", False, datetime(2025, 10, 14, 14, 33)),
        ("High risk detected in Karnal (Haryana)",
         "Stubble burning risk escalated to 54% as harvest activities peak across northern fields.",
         "High", "Karnal", False, datetime(2025, 10, 13, 11, 20)),
        ("Fire location detected near Hisar (Haryana)",
         "VIIRS satellite observation confirmed thermal hotspot with nominal confidence.",
         "High", "Hisar", True, datetime(2025, 10, 12, 21, 15)),
    ]

    for a in alerts_data:
        dist = district_map.get(a[3])
        db.add(Alert(
            district_id=dist.id if dist else None,
            title=a[0],
            message=a[1],
            severity=a[2],
            is_read=a[4],
            created_at=a[5]
        ))

    db.commit()
    logger.info(f"Database successfully seeded with {len(district_map)} districts and initial observations.")
