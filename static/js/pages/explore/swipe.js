// static/js/pages/explore/swipe.js — Swipe gesture handling
class SwipeCard {
    constructor(element, onSwiped) {
        this.element = element;
        this.isDragging = false;
        this.startX = 0;
        this.currentX = 0;
        this.onSwiped = onSwiped;
        this.hasSwiped = false;

        this.init();
    }

    init() {
        this.element.addEventListener('mousedown', this.startDrag.bind(this));
        this.element.addEventListener('mousemove', this.drag.bind(this));
        this.element.addEventListener('mouseup', this.endDrag.bind(this));
        this.element.addEventListener('mouseleave', this.endDrag.bind(this));

        this.element.addEventListener('touchstart', this.startDrag.bind(this));
        this.element.addEventListener('touchmove', this.drag.bind(this));
        this.element.addEventListener('touchend', this.endDrag.bind(this));
    }

    startDrag(e) {
        if (this.hasSwiped) return;
        this.isDragging = true;
        this.startX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
        this.element.classList.add('dragging');
    }

    drag(e) {
        if (!this.isDragging || this.hasSwiped) return;

        this.currentX = e.type.includes('mouse') ? e.clientX : e.touches[0].clientX;
        const diff = this.currentX - this.startX;

        this.element.style.transform = `translateX(${diff}px) rotate(${diff * 0.1}deg)`;

        this.element.classList.remove('drag-like', 'drag-dislike');
        if (diff > 30) {
            this.element.classList.add('drag-like');
        } else if (diff < -30) {
            this.element.classList.add('drag-dislike');
        }
    }

    endDrag() {
        if (!this.isDragging || this.hasSwiped) return;

        this.isDragging = false;
        this.element.classList.remove('dragging');

        const diff = this.currentX - this.startX;

        if (Math.abs(diff) > 100) {
            const liked = diff > 0;
            this.swipe(liked);
        } else {
            this.element.style.transform = '';
            this.element.classList.remove('drag-like', 'drag-dislike');
        }
    }

    flyOut(liked) {
        const direction = liked ? 1 : -1;
        this.element.style.transition = 'transform 0.4s ease, opacity 0.4s ease';
        this.element.style.transform = `translateX(${direction * 600}px) rotate(${direction * 30}deg)`;
        this.element.style.opacity = '0';
        this.element.style.pointerEvents = 'none';
    }

    async swipe(liked) {
        if (this.hasSwiped) return;
        this.hasSwiped = true;

        if (this.onSwiped) this.onSwiped();

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

        setTimeout(() => {
            this.element.remove();
        }, 400);
    }
}
