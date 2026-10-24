
import sqlite3
from pathlib import Path

# Database file project folder mein banegi
DB_PATH = Path(__file__).parent / "plant_care.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS plants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                species TEXT NOT NULL,
                pot_size TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id INTEGER,
                soil_moisture REAL,
                temperature REAL,
                humidity REAL,
                light_intensity REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plant_id) REFERENCES plants(id)
            )
        """)


def add_plant(name, species, pot_size):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO plants (name, species, pot_size)
            VALUES (?, ?, ?)
            """,
            (name, species, pot_size)
        )
        return cursor.lastrowid


def get_plants():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM plants ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def save_sensor_reading(
    plant_id,
    soil_moisture,
    temperature,
    humidity,
    light_intensity
):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sensor_readings
            (plant_id, soil_moisture, temperature, humidity, light_intensity)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                plant_id,
                soil_moisture,
                temperature,
                humidity,
                light_intensity
            )
        )


def get_sensor_readings(plant_id, limit=100):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM sensor_readings
            WHERE plant_id = ?
            ORDER BY recorded_at DESC
            LIMIT ?
            """,
            (plant_id, limit)
        ).fetchall()
        return [dict(row) for row in rows]