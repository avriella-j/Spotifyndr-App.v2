// static/js/pages/explore/card.js — Explore card rendering

let activeCards = [];
let swipeCount = 0;
const SESSION_LIMIT = 15;

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

        const swipeCard = new SwipeCard(card, () => onCardSwiped());
        activeCards.unshift(swipeCard);
    }

    function onCardSwiped() {
        activeCards.shift();
        swipeCount++;

        if (swipeCount >= SESSION_LIMIT) {
            showSessionComplete(container);
            return;
        }

        if (activeCards.length <= 2) {
            loadDeck();
        }
    }

    function showEmptyState(container) {
        if (container.querySelector('.swipe-empty-state')) return;
        const empty = document.createElement('div');
        empty.className = 'swipe-empty-state';
        empty.textContent = "You're all caught up — check back later for more.";
        container.appendChild(empty);
    }

    async function showSessionComplete(container) {
        container.innerHTML = '';
        const summary = document.createElement('div');
        summary.className = 'swipe-empty-state';
        summary.innerHTML = `<p>Nice swiping! Finding your taste pattern...</p>`;
        container.appendChild(summary);

        try {
            const result = await API.get('/swipes/taste-summary');
            summary.innerHTML = `
                <p class="swipe-session-message">${result.message}</p>
                <button class="btn btn-like" id="keep-swiping-btn" style="margin-top: var(--spacing-lg); width: auto; border-radius: var(--border-radius-md); padding: 0 var(--spacing-lg); font-size: var(--font-size-md);">
                    Keep swiping
                </button>
            `;
            document.getElementById('keep-swiping-btn')?.addEventListener('click', () => {
                swipeCount = 0;
                container.innerHTML = '';
                loadDeck();
            });
        } catch (error) {
            summary.innerHTML = `<p>Nice swiping! Check your stats anytime from your profile.</p>`;
        }
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
