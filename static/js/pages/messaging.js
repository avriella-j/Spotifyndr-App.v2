// static/js/pages/messaging.js — Messaging page logic
let currentConversationId = null;

// On DOM ready, load conversations
document.addEventListener('DOMContentLoaded', async () => {
    const conversationsList = document.getElementById('conversations-list');
    const messagesContainer = document.getElementById('messages');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    
    // Load conversations
    try {
        const conversations = await API.get('/messaging/conversations');
        
        conversations.forEach(conv => {
            const item = document.createElement('div');
            item.className = 'conversation-item';
            item.dataset.conversationId = conv.id;
            item.textContent = conv.participants.map(p => p.display_name).join(', ');
            item.addEventListener('click', () => loadConversation(conv.id));
            conversationsList.appendChild(item);
        });
    } catch (error) {
        Toast.error('Error', 'Failed to load conversations');
    }
    
    // Load conversation
    // Load messages for a conversation
    async function loadConversation(conversationId) {
        currentConversationId = conversationId;
        
        try {
            const messages = await API.get(`/messaging/conversations/${conversationId}/messages`);
            
            messagesContainer.innerHTML = '';
            messages.forEach(msg => {
                const div = document.createElement('div');
                div.className = `message ${msg.sender_id === currentUserId ? 'sent' : 'received'}`;
                div.textContent = msg.content;
                messagesContainer.appendChild(div);
            });
            
            // Join socket room
            socket.emit('join_conversation', { conversation_id: conversationId });
        } catch (error) {
            Toast.error('Error', 'Failed to load messages');
        }
    }
    
    // Send message
    // Send message on button click
    sendBtn.addEventListener('click', async () => {
        const content = messageInput.value.trim();
        if (!content || !currentConversationId) return;
        
        try {
            await API.post(`/messaging/conversations/${currentConversationId}/messages`, { content });
            messageInput.value = '';
        } catch (error) {
            Toast.error('Error', 'Failed to send message');
        }
    });
    
    // Listen for new messages
    // Listen for incoming messages via socket
    socket.on('new_message', (message) => {
        if (message.conversation_id === currentConversationId) {
            const div = document.createElement('div');
            div.className = `message ${message.sender_id === currentUserId ? 'sent' : 'received'}`;
            div.textContent = message.content;
            messagesContainer.appendChild(div);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    });
});
