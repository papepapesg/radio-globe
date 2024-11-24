import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_home_page():
    """Test that the home page loads successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_get_countries():
    """Test the countries API endpoint."""
    response = client.get("/api/countries")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        country = data[0]
        assert "name" in country
        assert "code" in country
        assert "stationcount" in country
        assert "flag" in country

def test_get_stations():
    """Test the stations API endpoint with a known country code."""
    response = client.get("/api/stations/US")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        station = data[0]
        assert "name" in station
        assert "url" in station
        assert "codec" in station
        assert "bitrate" in station
        assert "tags" in station

def test_invalid_country_code():
    """Test the stations API endpoint with an invalid country code."""
    response = client.get("/api/stations/INVALID")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_static_files():
    """Test that static files are being served."""
    response = client.get("/static/js/app.js")
    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
