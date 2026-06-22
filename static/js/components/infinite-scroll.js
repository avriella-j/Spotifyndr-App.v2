// Infinite scroll component
class InfiniteScroll {
    constructor(container, loadMore) {
        this.container = container;
        this.loadMore = loadMore;
        this.page = 1;
        this.loading = false;
        this.hasMore = true;
        
        this.init();
    }
    
    init() {
        window.addEventListener('scroll', Utils.debounce(() => {
            if (this.shouldLoad()) {
                this.load();
            }
        }, 200));
    }
    
    shouldLoad() {
        if (this.loading || !this.hasMore) return false;
        
        const scrollTop = window.scrollY;
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        
        return scrollTop + windowHeight >= documentHeight - 500;
    }
    
    async load() {
        this.loading = true;
        
        try {
            const items = await this.loadMore(this.page);
            
            if (items.length === 0) {
                this.hasMore = false;
            } else {
                this.page++;
            }
        } catch (error) {
            Toast.error('Error', 'Failed to load more items');
        } finally {
            this.loading = false;
        }
    }
}
