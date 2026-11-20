import sqlite3

from osdagbridge.core.data.project_location.database import Database


def test_partial_weather_db_is_reseeded(tmp_path):
    """A legacy DB with only stations must be reseeded on connect.

    Location dropdowns are built from temperature_data, so a stations-only
    DB silently leaves the Project Location dialog with no selectable state.
    """
    db_path = tmp_path / "weather.sqlite"
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE stations ("
        "state TEXT NOT NULL, station TEXT NOT NULL, "
        "latitude REAL, longitude REAL, UNIQUE (state, station))"
    )
    conn.execute(
        "INSERT INTO stations VALUES ('Karnataka', 'Bangalore (A)', 12.95, 77.68)"
    )
    conn.commit()
    conn.close()

    db = Database(str(db_path))
    db.connect()
    try:
        assert "Karnataka" in db.get_states_with_temperature()
        weather = db.get_weather_data_by_state_station("Karnataka", "Bangalore (A)")
        assert weather is not None
        assert weather["wind_speed"] is not None
        assert weather["zone"] is not None
        assert weather["max_temp"] is not None
        assert weather["min_temp"] is not None
    finally:
        db.close()
