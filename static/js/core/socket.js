// static/js/core/socket.js — Socket.IO client setup
const socket = io();

// Handle successful connection
socket.on('connect', () => {
    console.log('Connected to server');
});

// Handle disconnection
socket.on('disconnect', () => {
    console.log('Disconnected from server');
});

// Incoming chat message handler
socket.on('new_message', (message) => {
    // Handle new message
    console.log('New message:', message);
});

// In-app notification handler
socket.on('notification', (notification) => {
    // Handle notification
    Toast.show(notification.title, notification.message);
});
