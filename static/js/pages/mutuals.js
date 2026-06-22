// static/js/pages/mutuals.js — Mutuals page logic
// On DOM ready, fetch mutuals and set up follow buttons
document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('mutuals');
    
    try {
        const mutuals = await API.get('/mutuals');
        
        mutuals.forEach(user => {
            const card = document.createElement('div');
            card.className = 'user-card';
            card.dataset.userId = user.id;
            card.innerHTML = `
                <img src="${user.image_url}" alt="${user.display_name}" class="user-image">
                <div class="user-info">
                    <h3>${user.display_name}</h3>
                    <button class="btn btn-follow" data-user-id="${user.id}">Follow</button>
                </div>
            `;
            container.appendChild(card);
        });
        
        // Follow button handlers
        container.querySelectorAll('.btn-follow').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const userId = e.target.dataset.userId;
                
                try {
                    await API.post(`/follows/${userId}`);
                    e.target.textContent = 'Following';
                    e.target.disabled = true;
                    Toast.success('Success', 'User followed');
                } catch (error) {
                    Toast.error('Error', 'Failed to follow user');
                }
            });
        });
    } catch (error) {
        Toast.error('Error', 'Failed to load mutuals');
    }
});
