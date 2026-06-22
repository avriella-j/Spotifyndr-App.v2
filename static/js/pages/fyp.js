// static/js/pages/fyp.js — "For You" recommendations
// On DOM ready, fetch recommendations
document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('recommendations');
    
    try {
        const recommendations = await API.get('/fyp?limit=10');
        
        recommendations.forEach(rec => {
            const card = document.createElement('div');
            card.className = 'track-card';
            card.innerHTML = `
                <img src="${rec.image_url}" alt="${rec.name}" class="track-image">
                <div class="track-info">
                    <h3>${rec.name}</h3>
                    <p>${rec.artist}</p>
                </div>
                <button class="btn btn-play">▶</button>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        Toast.error('Error', 'Failed to load recommendations');
    }
});
