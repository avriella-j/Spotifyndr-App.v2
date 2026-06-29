// static/js/pages/explore/card.js — Explore card rendering

let activeCards = [];
let swipeCount = 0;
let deckPool = [];
let deckPoolIndex = 0;
let discoveryOffset = 0;
let seenTrackIds = new Set();
const RENDER_AHEAD = 3;
const WRAPPED_MIN_SWIPES = 5;
const DISCOVERY_BATCH_SIZE = 20;

document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('swipe-container');
    const wrappedBtn = document.getElementById('wrapped-btn');

    async function fetchOwnLibraryPool() {
        try {
            const content = await API.get('/swipes/deck');
            return content || [];
        } catch (error) {
            return [];
        }
    }

    async function fetchDiscoveryBatch() {
        try {
            const excludeIds = Array.from(seenTrackIds).join(',');
            const batch = await API.get(`/swipes/discover?exclude_ids=${excludeIds}&offset=${discoveryOffset}`);
            discoveryOffset += DISCOVERY_BATCH_SIZE;
            return batch || [];
        } catch (error) {
            return [];
        }
    }

    function nextPoolItem() {
        if (deckPoolIndex < deckPool.length) {
            const item = deckPool[deckPoolIndex];
            deckPoolIndex++;
            return item;
        }
        return null;
    }

    function renderCard(item, container) {
        if (seenTrackIds.has(item.id)) return;
        seenTrackIds.add(item.id);

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

    async function fillStack(container) {
        while (activeCards.length < RENDER_AHEAD) {
            let item = nextPoolItem();
            if (!item) {
                const batch = await fetchDiscoveryBatch();
                if (batch.length === 0) break;
                deckPool = deckPool.concat(batch);
                item = nextPoolItem();
                if (!item) break;
            }
            renderCard(item, container);
        }
    }

    async function onCardSwiped(container) {
        activeCards.shift();
        swipeCount++;
        updateWrappedButton();
        await fillStack(container);
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
        empty.textContent = "You've explored everything we could find — check back later for more.";
        container.appendChild(empty);
    }

    async function showWrapped() {
        const overlay = document.createElement('div');
        overlay.className = 'wrapped-overlay';
        overlay.innerHTML = `<p class="swipe-session-message">Finding your taste pattern...</p>`;
        document.body.appendChild(overlay);

        try {
            const result = await API.get('/swipes/taste-summary');
            const artistList = (result.artists || [])
                .map(a => `<li>${a.name}</li>`)
                .join('');
            overlay.innerHTML = `
                <div class="wrapped-card">
                    <h2>Swipr Wrapped</h2>
                    <p class="swipe-session-message">${result.message}</p>
                    ${artistList ? `<ul class="wrapped-genre-list">${artistList}</ul>` : ''}
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

    deckPool = await fetchOwnLibraryPool();
    if (deckPool.length === 0) {
        const batch = await fetchDiscoveryBatch();
        deckPool = batch;
    }
    if (deckPool.length === 0) {
        showEmptyState(container);
    } else {
        await fillStack(container);
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
