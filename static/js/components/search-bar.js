// static/js/components/search-bar.js — Search bar component
// Debounced search input with dropdown results
class SearchBar {
    // Store input reference and set up state
    constructor(input) {
        this.input = input;
        this.resultsContainer = null;
        this.debounceTimer = null;
        
        this.init();
    }
    
    // Set up debounced input listener
    init() {
        this.input.addEventListener('input', (e) => {
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                this.search(e.target.value);
            }, 300);
        });
    }
    
    // Query backend and show/hide results
    async search(query) {
        if (query.length < 2) {
            this.hideResults();
            return;
        }
        
        try {
            const results = await API.get(`/search?q=${query}`);
            this.showResults(results);
        } catch (error) {
            console.error('Search failed:', error);
        }
    }
    
    // Render result dropdown below input
    showResults(results) {
        if (!this.resultsContainer) {
            this.resultsContainer = document.createElement('div');
            this.resultsContainer.className = 'search-results';
            this.input.parentNode.appendChild(this.resultsContainer);
        }
        
        this.resultsContainer.innerHTML = results.map(item => `
            <div class="search-result" data-id="${item.id}">
                <img src="${item.image_url}" alt="${item.name}">
                <span>${item.name}</span>
            </div>
        `).join('');
        
        this.resultsContainer.style.display = 'block';
    }
    
    // Hide the results dropdown
    hideResults() {
        if (this.resultsContainer) {
            this.resultsContainer.style.display = 'none';
        }
    }
}
