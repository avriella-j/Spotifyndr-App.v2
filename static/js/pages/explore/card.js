// static/js/pages/explore/card.js — Explore card rendering
// On DOM ready, fetch content and render swipe cards
document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('swipe-container');
    
    try {
        const content = await API.get('/explore?limit=10');
        
        content.forEach(item => {
            const card = document.createElement('div');
            card.className = 'swipe-card';
            card.dataset.contentId = item.id;
            card.innerHTML = `
                <div class="swipe-card-content">
                    <img src="${item.image_url}" alt="${item.name}" class="swipe-card-image">
                    <div class="swipe-card-info">
                        <h3>${item.name}</h3>
                        <p>${item.artist}</p>
                    </div>
                </div>
            `;
            container.appendChild(card);
            
            new SwipeCard(card);
        });
    } catch (error) {
        Toast.error('Error', 'Failed to load explore content');
    }
    
    // Button handlers
    document.getElementById('like-btn')?.addEventListener('click', () => {
        const card = container.querySelector('.swipe-card:last-child');
        if (card) {
            new SwipeCard(card).swipe(true);
        }
    });
    
    document.getElementById('dislike-btn')?.addEventListener('click', () => {
        const card = container.querySelector('.swipe-card:last-child');
        if (card) {
            new SwipeCard(card).swipe(false);
        }
    });
});
