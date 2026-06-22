// static/js/pages/explore/swipe.js — Swipe gesture handling
// Drag-to-swipe card class
class SwipeCard {
    // Store card element and drag state
    constructor(element) {
        this.element = element;
        this.isDragging = false;
        this.startX = 0;
        this.currentX = 0;
        
        this.init();
    }
    
    // Attach mouse and touch event listeners
    init() {
        this.element.addEventListener('mousedown', this.startDrag.bind(this));
        this.element.addEventListener('mousemove', this.drag.bind(this));
        this.element.addEventListener('mouseup', this.endDrag.bind(this));
        this.element.addEventListener('mouseleave', this.endDrag.bind(this));
        
        // Touch events
        this.element.addEventListener('touchstart', this.startDrag.bind(this));
        this.element.addEventListener('touchmove', this.drag.bind(this));
        this.element.addEventListener('touchend', this.endDrag.bind(this));
    }
    
    // Record drag start position
    startDrag(e) {
        this.isDragging = true;
        this.startX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
        this.element.classList.add('dragging');
    }
    
    // Update card position during drag
    drag(e) {
        if (!this.isDragging) return;
        
        this.currentX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
        const diff = this.currentX - this.startX;
        
        this.element.style.transform = `translateX(${diff}px) rotate(${diff * 0.1}deg)`;
    }
    
    // Complete swipe or reset card position
    endDrag() {
        if (!this.isDragging) return;
        
        this.isDragging = false;
        this.element.classList.remove('dragging');
        
        const diff = this.currentX - this.startX;
        
        if (Math.abs(diff) > 100) {
            // Swipe completed
            const liked = diff > 0;
            this.swipe(liked);
        } else {
            // Reset position
            this.element.style.transform = '';
        }
    }
    
    // Send swipe result to backend and remove card
    async swipe(liked) {
        const contentId = this.element.dataset.contentId;
        
        try {
            await API.post('/explore/swipe', { content_id: contentId, liked });
            this.element.remove();
        } catch (error) {
            Toast.error('Error', 'Failed to record swipe');
        }
    }
}
