# Radio Globe 🌍 🎵

A modern web application for discovering and listening to radio stations from around the world. Built with FastAPI and vanilla JavaScript, Radio Globe provides an intuitive tile-based interface for exploring global radio stations.

## Features

- 🗺️ Visual country-based navigation with flag backgrounds
- 🔍 Real-time country search functionality
- 📻 High-quality radio station streaming
- 🎨 Modern, responsive dark theme design
- 📊 Station count visualization
- 🏷️ Station metadata display (bitrate, codec, tags)

## Tech Stack

- **Backend:**
  - FastAPI (Python web framework)
  - httpx (Async HTTP client)
  - Jinja2 (Template engine)
  - uvicorn (ASGI server)

- **Frontend:**
  - Vanilla JavaScript (No framework dependencies)
  - CSS Grid for responsive layout
  - HTML5 Audio API

- **APIs:**
  - Radio Browser API (Station data)
  - REST Countries API (Country flags)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/radio-globe.git
   cd radio-globe
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the FastAPI server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

## Project Structure

```
radio-globe/
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI application
├── static/
│   ├── css/
│   │   └── styles.css   # Application styles
│   └── js/
│       └── app.js       # Frontend JavaScript
├── templates/
│   └── index.html       # Main HTML template
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## API Endpoints

- `GET /`: Main application page
- `GET /api/countries`: List of countries with station counts and flags
- `GET /api/stations/{country_code}`: Radio stations for a specific country

## Performance Optimizations

- Parallel flag fetching using asyncio
- Country flag caching
- Station sorting by bitrate
- Limited to top 100 stations per country
- Efficient grid-based UI rendering

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Radio Browser API](https://api.radio-browser.info/) for providing radio station data
- [REST Countries API](https://restcountries.com/) for country information and flags

## Support

For support, please open an issue in the GitHub repository.

## Utilities

### Transfer YouTube Music Likes to Spotify

The script `transfer_youtube_to_spotify.py` moves your liked songs from YouTube Music into a Spotify playlist.

1. Ensure `ytmusicapi` and `spotipy` are installed (`pip install -r requirements.txt`).
2. Create a headers authentication JSON for YouTube Music via `ytmusicapi.setup_oauth()`.
3. Set the Spotify environment variables `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, and `SPOTIFY_REDIRECT_URI`.
4. Run the script:
   ```bash
   python transfer_youtube_to_spotify.py --playlist "My YT Likes" --headers headers_auth.json
   ```

The script will create the playlist if it does not already exist and add any matching tracks.
