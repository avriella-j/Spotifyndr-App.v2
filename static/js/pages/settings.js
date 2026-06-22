// static/js/pages/settings.js — Settings page logic
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('settings-form');
    const deleteBtn = document.getElementById('delete-account');
    
    // Save settings
    // Save settings on form submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        try {
            await API.put('/settings', data);
            Toast.success('Success', 'Settings saved');
        } catch (error) {
            Toast.error('Error', 'Failed to save settings');
        }
    });
    
    // Delete account
    // Delete account with confirmation
    deleteBtn.addEventListener('click', async () => {
        if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
            return;
        }
        
        try {
            await API.delete('/users/me');
            window.location.href = '/';
        } catch (error) {
            Toast.error('Error', 'Failed to delete account');
        }
    });
});
