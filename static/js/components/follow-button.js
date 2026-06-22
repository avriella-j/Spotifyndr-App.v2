// static/js/components/follow-button.js — Follow button component
// Toggle follow/unfollow for a user
class FollowButton {
    // Store button reference and user ID
    constructor(button) {
        this.button = button;
        this.userId = button.dataset.userId;
        this.isFollowing = false;
        
        this.init();
    }
    
    // Attach click handler
    init() {
        this.button.addEventListener('click', () => this.toggleFollow());
    }
    
    // Follow or unfollow based on current state
    async toggleFollow() {
        if (this.isFollowing) {
            try {
                await API.delete(`/follows/${this.userId}`);
                this.isFollowing = false;
                this.button.textContent = 'Follow';
                this.button.classList.remove('following');
                Toast.success('Success', 'User unfollowed');
            } catch (error) {
                Toast.error('Error', 'Failed to unfollow user');
            }
        } else {
            try {
                await API.post(`/follows/${this.userId}`);
                this.isFollowing = true;
                this.button.textContent = 'Following';
                this.button.classList.add('following');
                Toast.success('Success', 'User followed');
            } catch (error) {
                Toast.error('Error', 'Failed to follow user');
            }
        }
    }
}

// Initialize follow buttons
document.querySelectorAll('.btn-follow').forEach(btn => {
    new FollowButton(btn);
});
