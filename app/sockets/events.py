# app/sockets/events.py — SocketIO event handler registration

from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room
from app.services.messaging_service import MessagingService


def register_socket_events(socketio):
    """Register SocketIO event handlers."""
    
    # Join user room on connection
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        if current_user.is_authenticated:
            join_room(f'user_{current_user.id}')
            emit('connected', {'user_id': current_user.id})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        if current_user.is_authenticated:
            leave_room(f'user_{current_user.id}')
    
    @socketio.on('join_conversation')
    def handle_join_conversation(data):
        """Join a conversation room."""
        conversation_id = data.get('conversation_id')
        if current_user.is_authenticated:
            join_room(f'conversation_{conversation_id}')
    
    @socketio.on('leave_conversation')
    def handle_leave_conversation(data):
        """Leave a conversation room."""
        conversation_id = data.get('conversation_id')
        if current_user.is_authenticated:
            leave_room(f'conversation_{conversation_id}')
    
    # Send message and emit to conversation room + notify recipient
    @socketio.on('send_message')
    def handle_send_message(data):
        """Handle sending a message."""
        if not current_user.is_authenticated:
            return
        
        conversation_id = data.get('conversation_id')
        content = data.get('content')
        
        message = MessagingService.send_message(
            current_user.id,
            conversation_id,
            content
        )
        
        if message:
            emit('new_message', message.to_dict(), room=f'conversation_{conversation_id}')
            
            # Notify recipient
            emit('notification', {
                'type': 'message',
                'title': 'New Message',
                'message': f'{current_user.display_name} sent you a message'
            }, room=f'user_{message.recipient_id}')
