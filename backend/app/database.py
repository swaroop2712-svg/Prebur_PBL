import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("preburn.database")

# Configure database engine
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency that provides an independent database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and run automatic seeder if empty."""
    from app.models import (  # noqa: F401
        State,
        District,
        RiskPrediction,
        FireDetection,
        WeatherForecast,
        Alert
    )
    from app.services.seed_service import seed_initial_data

    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created successfully.")

    # Safe migration check for existing SQLite tables
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            if settings.DATABASE_URL.startswith("sqlite"):
                info = conn.execute(text("PRAGMA table_info(districts)")).fetchall()
                col_names = [r[1] for r in info]
                if col_names and "officer_name" not in col_names:
                    conn.execute(text("ALTER TABLE districts ADD COLUMN officer_name VARCHAR(100) DEFAULT 'Agriculture Development Officer'"))
                    conn.commit()
                if col_names and "officer_phone" not in col_names:
                    conn.execute(text("ALTER TABLE districts ADD COLUMN officer_phone VARCHAR(20) DEFAULT '+919876543210'"))
                    conn.commit()
    except Exception as ex:
        logger.debug(f"Column check notice: {ex}")

    # Populate seed data
    db = SessionLocal()
    try:
        seed_initial_data(db)
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()
