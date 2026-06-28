// static/js/pages/explore/card.js — Explore card rendering
// On DOM ready, fetch content and render swipe cards

let activeCards = [];

document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('swipe-container');

    async function loadDeck() {
        try {
            const content = await API.get('/swipes/deck');

            if (!content || content.length === 0) {
                if (activeCards.length === 0) {
                    showEmptyState(container);
                }
                return;
            }

            content.forEach(item => renderCard(item, container));
        } catch (error) {
            Toast.error('Error', 'Failed to load explore content');
        }
    }

    function renderCard(item, container) {
        const card = document.createElement('div');
        card.className = 'swipe-card';
        card.dataset.contentId = item.id;
        card.dataset.contentType = item.type || 'track';
        card.innerHTML = `
            <div class="swipe-card-content">
                <img src="${item.image_url || ''}" alt="${item.name}" class="swipe-card-image">
                <div class="swipe-card-info">
                    <h3>${item.name}</h3>
                    <p>${item.artist}</p>
                </div>
            </div>
        `;

        container.prepend(card);

        const swipeCard = new SwipeCard(card, () => onCardRemoved(container));
        activeCards.unshift(swipeCard);
    }

    function onCardRemoved(container) {
        activeCards.shift();
        if (activeCards.length <= 2) {
            loadDeck();
        }
        if (activeCards.length === 0) {
            showEmptyState(container);
        }
    }

    function showEmptyState(container) {
        if (container.querySelector('.swipe-empty-state')) return;
        const empty = document.createElement('div');
        empty.className = 'swipe-empty-state';
        empty.textContent = "You're all caught up — check back later for more.";
        container.appendChild(empty);
    }

    await loadDeck();

    document.getElementById('like-btn')?.addEventListener('click', () => {
        if (activeCards.length > 0) {
            activeCards[0].swipe(true);
        }
    });

    document.getElementById('dislike-btn')?.addEventListener('click', () => {
        if (activeCards.length > 0) {
            activeCards[0].swipe(false);
        }
    });
});
