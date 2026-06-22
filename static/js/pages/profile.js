// static/js/pages/profile.js — Profile page logic
// On DOM ready, fetch and render profile data
document.addEventListener('DOMContentLoaded', async () => {
    const topTracksContainer = document.getElementById('top-tracks');
    const topArtistsContainer = document.getElementById('top-artists');
    
    try {
        // Load top tracks
        const topTracks = await API.get('/users/me/top-tracks');
        topTracks.forEach(track => {
            const card = document.createElement('div');
            card.className = 'track-card';
            card.innerHTML = `
                <img src="${track.image_url}" alt="${track.name}" class="track-image">
                <div class="track-info">
                    <h3>${track.name}</h3>
                    <p>${track.artist}</p>
                </div>
            `;
            topTracksContainer.appendChild(card);
        });
        
        // Load top artists
        const topArtists = await API.get('/users/me/top-artists');
        topArtists.forEach(artist => {
            const card = document.createElement('div');
            card.className = 'artist-card';
            card.innerHTML = `
                <img src="${artist.image_url}" alt="${artist.name}" class="artist-image">
                <div class="artist-info">
                    <h3>${artist.name}</h3>
                    <p>${Utils.formatNumber(artist.followers)} followers</p>
                </div>
            `;
            topArtistsContainer.appendChild(card);
        });
    } catch (error) {
        Toast.error('Error', 'Failed to load profile data');
    }
});
