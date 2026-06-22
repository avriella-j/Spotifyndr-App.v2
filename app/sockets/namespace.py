# app/sockets/namespace.py — SocketIO namespace for messaging

from flask_socketio import Namespace, emit, join_room, leave_room
from flask_login import current_user


class MessagingNamespace(Namespace):
    """SocketIO namespace for messaging."""
    
    # Join user's personal room on connect
    def on_connect(self):
        """Handle connection to messaging namespace."""
        if current_user.is_authenticated:
            join_room(f'user_{current_user.id}')
            emit('connected', {'namespace': '/messaging'})
    
    # Leave user's personal room on disconnect
    def on_disconnect(self):
        """Handle disconnection from messaging namespace."""
        if current_user.is_authenticated:
            leave_room(f'user_{current_user.id}')
    
    def on_join_conversation(self, data):
        """Join a specific conversation room."""
        conversation_id = data.get('conversation_id')
        if current_user.is_authenticated:
            join_room(f'conversation_{conversation_id}')
            emit('joined_conversation', {'conversation_id': conversation_id})
    
    def on_leave_conversation(self, data):
        """Leave a specific conversation room."""
        conversation_id = data.get('conversation_id')
        if current_user.is_authenticated:
            leave_room(f'conversation_{conversation_id}')
            emit('left_conversation', {'conversation_id': conversation_id})
