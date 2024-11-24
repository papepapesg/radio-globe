// Global UI object to manage DOM elements
const UI = {
    countryGrid: document.getElementById('countryGrid'),
    searchInput: document.getElementById('searchInput'),
    stationPanel: document.getElementById('stationPanel'),
    stationList: document.getElementById('stationList'),
    selectedCountry: document.getElementById('selectedCountry'),
    playerPanel: document.getElementById('playerPanel'),
    currentStation: document.getElementById('currentStation'),
    audioPlayer: document.getElementById('audioPlayer'),
    closePlayer: document.getElementById('closePlayer'),
    loading: document.querySelector('.loading')
};

// Close player when close button is clicked
UI.closePlayer.addEventListener('click', () => {
    UI.audioPlayer.pause();
    UI.playerPanel.style.display = 'none';
});

// Function to play a station
function playStation(station) {
    UI.currentStation.textContent = station.name;
    UI.audioPlayer.src = station.url;
    UI.playerPanel.style.display = 'flex';
    UI.audioPlayer.play().catch(error => {
        console.error('Error playing station:', error);
        alert('Error playing station. Please try another one.');
    });
}

// Function to create a station element
function createStationElement(station) {
    const div = document.createElement('div');
    div.className = 'station-card';
    div.innerHTML = `
        <div class="station-info">
            <div class="station-details">
                <h3 class="station-name">${station.name}</h3>
                <p class="station-tags">${station.tags.filter(t => t).join(', ') || 'No tags'}</p>
                <p class="station-codec">${station.codec} - ${station.bitrate}kbps</p>
            </div>
        </div>
    `;
    div.addEventListener('click', () => playStation(station));
    return div;
}

// Function to create a country tile
function createCountryTile(country) {
    const tile = document.createElement('div');
    tile.className = 'country-tile';
    tile.style.backgroundImage = country.flag ? `url(${country.flag})` : 'none';
    
    const overlay = document.createElement('div');
    overlay.className = 'country-overlay';
    
    overlay.innerHTML = `
        <div class="station-count">${country.stationcount}</div>
        <div class="country-name">${country.name}</div>
    `;
    
    tile.appendChild(overlay);
    
    tile.addEventListener('click', () => showStations(country.code, country.name));
    
    return tile;
}

// Function to show stations for a country
async function showStations(countryCode, countryName) {
    console.log(`Loading stations for ${countryName} (${countryCode})`);
    
    UI.selectedCountry.textContent = `Loading stations for ${countryName}...`;
    UI.stationPanel.style.display = 'block';
    UI.stationList.innerHTML = '';

    try {
        const response = await fetch(`/api/stations/${countryCode}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const stations = await response.json();
        console.log('Received stations:', stations);
        
        UI.selectedCountry.textContent = `${countryName} (${stations.length} stations)`;
        
        if (!Array.isArray(stations) || stations.length === 0) {
            UI.stationList.innerHTML = '<p class="no-stations">No stations found for this country.</p>';
            return;
        }

        stations.forEach(station => {
            UI.stationList.appendChild(createStationElement(station));
        });
    } catch (error) {
        console.error('Error loading stations:', error);
        UI.stationList.innerHTML = `<p class="error">Error loading stations: ${error.message}</p>`;
    }
}

// Function to filter countries
function filterCountries(countries, searchTerm) {
    searchTerm = searchTerm.toLowerCase();
    return countries.filter(country => 
        country.name.toLowerCase().includes(searchTerm) ||
        country.code.toLowerCase().includes(searchTerm)
    );
}

// Function to render country grid
function renderCountryGrid(countries) {
    UI.countryGrid.innerHTML = '';
    countries.forEach(country => {
        UI.countryGrid.appendChild(createCountryTile(country));
    });
}

// Initialize the app
async function initializeApp() {
    UI.loading.style.display = 'block';
    
    try {
        const response = await fetch('/api/countries');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const countries = await response.json();
        console.log('Loaded countries:', countries);
        
        // Store countries globally for search
        window.countries = countries;
        
        // Render initial grid
        renderCountryGrid(countries);
        
        // Set up search
        UI.searchInput.addEventListener('input', (e) => {
            const filtered = filterCountries(window.countries, e.target.value);
            renderCountryGrid(filtered);
        });
        
    } catch (error) {
        console.error('Error initializing app:', error);
        UI.countryGrid.innerHTML = `
            <div style="color: white; text-align: center; padding: 20px;">
                Error loading countries. Please refresh the page.
            </div>
        `;
    } finally {
        UI.loading.style.display = 'none';
    }
}

// Start the app when the page loads
document.addEventListener('DOMContentLoaded', initializeApp);
