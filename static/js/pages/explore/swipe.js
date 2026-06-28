// static/js/pages/explore/swipe.js — Swipe gesture handling
// Drag-to-swipe card class
class SwipeCard {
    // Store card element and drag state
    constructor(element, onSwiped) {
        this.element = element;
        this.isDragging = false;
        this.startX = 0;
        this.currentX = 0;
        this.onSwiped = onSwiped; // callback invoked after a successful swipe

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

        // Live color feedback while dragging
        this.element.classList.remove('drag-like', 'drag-dislike');
        if (diff > 30) {
            this.element.classList.add('drag-like');
        } else if (diff < -30) {
            this.element.classList.add('drag-dislike');
        }
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
            this.element.classList.remove('drag-like', 'drag-dislike');
        }
    }

    // Animate the card flying off screen in the swipe direction
    flyOut(liked) {
        const direction = liked ? 1 : -1;
        this.element.style.transition = 'transform 0.4s ease, opacity 0.4s ease';
        this.element.style.transform = `translateX(${direction * 600}px) rotate(${direction * 30}deg)`;
        this.element.style.opacity = '0';
    }

    // Send swipe result to backend and remove card
    async swipe(liked) {
        const contentId = this.element.dataset.contentId;
        const contentType = this.element.dataset.contentType || 'track';

        this.flyOut(liked);

        try {
            await API.post('/swipes', {
                content_id: contentId,
                content_type: contentType,
                liked: liked,
            });
        } catch (error) {
            Toast.error('Error', 'Failed to record swipe');
        }

        // Remove the card after the fly-out animation finishes, then let
        // the caller know so it can reveal the next card / load more
        setTimeout(() => {
            this.element.remove();
            if (this.onSwiped) this.onSwiped();
        }, 400);
    }
}
