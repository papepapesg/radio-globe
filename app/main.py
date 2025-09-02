from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.requests import Request
import httpx
import asyncio
from typing import List, Dict, Optional
import logging
import os
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Radio Globe", description="A global radio station discovery platform")

# Mount static files and templates
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
templates = Jinja2Templates(directory=os.path.join(PROJECT_ROOT, "templates"))

@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    full_path = os.path.join(STATIC_DIR, file_path)
    if os.path.isfile(full_path):
        with open(full_path, "rb") as f:
            content = f.read()
        media_type = "application/octet-stream"
        if full_path.endswith(".js"):
            media_type = "application/javascript"
        elif full_path.endswith(".css"):
            media_type = "text/css"
        elif full_path.endswith(".html"):
            media_type = "text/html"
        return Response(content=content, media_type=media_type)
    return Response(status_code=404)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
RADIO_BROWSER_API = "https://de1.api.radio-browser.info/json"
COUNTRIES_API = "https://restcountries.com/v3.1/alpha"
USER_AGENT = "RadioGlobe/1.0"

# Cache for country flags
flag_cache: Dict[str, str] = {}

async def fetch_country_flag(client: httpx.AsyncClient, country_code: str) -> Optional[str]:
    """Fetch country flag URL from REST Countries API."""
    if country_code in flag_cache:
        return flag_cache[country_code]
    
    try:
        response = await client.get(f"{COUNTRIES_API}/{country_code}")
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                flag_url = data[0]["flags"]["png"]
                flag_cache[country_code] = flag_url
                return flag_url
    except Exception as e:
        logger.error(f"Error fetching flag for {country_code}: {str(e)}")
    
    return None

async def get_stations_by_country(country_code: str) -> List[Dict]:
    """Fetch radio stations for a specific country."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(
                f"{RADIO_BROWSER_API}/stations/bycountrycodeexact/{country_code}",
                headers={"User-Agent": USER_AGENT}
            )
            response.raise_for_status()

            stations = response.json()
            # Sort by bitrate and limit to top 100
            stations.sort(key=lambda x: int(x.get("bitrate", 0) or 0), reverse=True)
            return [
                {
                    "name": station["name"],
                    "url": station["url"],
                    "codec": station["codec"],
                    "bitrate": station["bitrate"],
                    "tags": station.get("tags", "").split(",") if station.get("tags") else []
                }
                for station in stations[:100]
                if station["url"] and station["name"]
            ]
        except httpx.HTTPError as e:
            logger.error(f"Error fetching stations for {country_code}: {e}")
            return []

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main application page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/countries")
async def get_countries():
    """Get list of countries with their station counts and flags."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(
                f"{RADIO_BROWSER_API}/countries",
                headers={"User-Agent": USER_AGENT}
            )
            response.raise_for_status()
            countries = response.json()

            # Filter and sort countries by station count
            valid_countries = [
                country for country in countries
                if country["name"] and country["iso_3166_1"]
                and int(country.get("stationcount", 0) or 0) > 0
            ]
            valid_countries.sort(key=lambda x: int(x.get("stationcount", 0) or 0), reverse=True)

            # Fetch flags in parallel
            tasks = [
                fetch_country_flag(client, country["iso_3166_1"])
                for country in valid_countries
            ]
            flags = await asyncio.gather(*tasks)

            return [
                {
                    "name": country["name"],
                    "code": country["iso_3166_1"],
                    "stationcount": int(country.get("stationcount", 0) or 0),
                    "flag": flag
                }
                for country, flag in zip(valid_countries, flags)
            ]
        except httpx.HTTPError as e:
            logger.error(f"Error fetching countries: {e}")
            return []

@app.get("/api/stations/{country_code}")
async def get_stations(country_code: str):
    """Get radio stations for a specific country."""
    return await get_stations_by_country(country_code)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
