// static/js/pages/explore/card.js — Explore card rendering

let activeCards = [];
let swipeCount = 0;
let deckPool = [];
let deckPoolIndex = 0;
const RENDER_AHEAD = 3;
const WRAPPED_MIN_SWIPES = 5;

document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('swipe-container');
    const wrappedBtn = document.getElementById('wrapped-btn');

    async function fetchPool() {
        try {
            const content = await API.get('/swipes/deck');
            return content || [];
        } catch (error) {
            Toast.error('Error', 'Failed to load explore content');
            return [];
        }
    }

    function nextPoolItem() {
        if (deckPool.length === 0) return null;
        const item = deckPool[deckPoolIndex % deckPool.length];
        deckPoolIndex++;
        return item;
    }

    function renderNextCard(container) {
        const item = nextPoolItem();
        if (!item) return;

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

        const swipeCard = new SwipeCard(card, () => onCardSwiped(container));
        activeCards.unshift(swipeCard);
    }

    function fillStack(container) {
        while (activeCards.length < RENDER_AHEAD && deckPool.length > 0) {
            renderNextCard(container);
        }
    }

    function onCardSwiped(container) {
        activeCards.shift();
        swipeCount++;
        updateWrappedButton();
        fillStack(container);
    }

    function updateWrappedButton() {
        if (!wrappedBtn) return;
        if (swipeCount >= WRAPPED_MIN_SWIPES) {
            wrappedBtn.classList.remove('hidden');
        }
    }

    function showEmptyState(container) {
        if (container.querySelector('.swipe-empty-state')) return;
        const empty = document.createElement('div');
        empty.className = 'swipe-empty-state';
        empty.textContent = "No tracks available to swipe on right now.";
        container.appendChild(empty);
    }

    async function showWrapped() {
        const overlay = document.createElement('div');
        overlay.className = 'wrapped-overlay';
        overlay.innerHTML = `<p class="swipe-session-message">Finding your taste pattern...</p>`;
        document.body.appendChild(overlay);

        try {
            const result = await API.get('/swipes/taste-summary');
            const genreList = (result.genres || [])
                .map(g => `<li>${g.genre}</li>`)
                .join('');
            overlay.innerHTML = `
                <div class="wrapped-card">
                    <h2>Swipr Wrapped</h2>
                    <p class="swipe-session-message">${result.message}</p>
                    ${genreList ? `<ul class="wrapped-genre-list">${genreList}</ul>` : ''}
                    <p class="wrapped-swipe-count">${swipeCount} swipes this session</p>
                    <button class="btn btn-like" id="close-wrapped-btn">Keep swiping</button>
                </div>
            `;
        } catch (error) {
            overlay.innerHTML = `
                <div class="wrapped-card">
                    <h2>Swipr Wrapped</h2>
                    <p class="swipe-session-message">Couldn't load your stats right now — try again in a bit.</p>
                    <button class="btn btn-like" id="close-wrapped-btn">Close</button>
                </div>
            `;
        }

        document.getElementById('close-wrapped-btn')?.addEventListener('click', () => {
            overlay.remove();
        });
    }

    deckPool = await fetchPool();
    if (deckPool.length === 0) {
        showEmptyState(container);
    } else {
        fillStack(container);
    }

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

    wrappedBtn?.addEventListener('click', showWrapped);
});
