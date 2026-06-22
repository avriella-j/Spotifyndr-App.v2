from flask import jsonify, request
from flask_login import login_required, current_user
from app.services.messaging_service import MessagingService


@login_required
def get_conversations():
    """Get user's conversations."""
    conversations = MessagingService.get_user_conversations(current_user.id)
    return jsonify([c.to_dict() for c in conversations])


@login_required
def create_conversation():
    """Create a new conversation."""
    data = request.get_json()
    participant_id = data.get('participant_id')
    
    conversation = MessagingService.create_conversation(current_user.id, participant_id)
    return jsonify(conversation.to_dict())


@login_required
def get_messages(conversation_id):
    """Get messages from a conversation."""
    messages = MessagingService.get_conversation_messages(conversation_id)
    return jsonify([m.to_dict() for m in messages])


@login_required
def send_message(conversation_id):
    """Send a message to a conversation."""
    data = request.get_json()
    content = data.get('content')
    
    message = MessagingService.send_message(current_user.id, conversation_id, content)
    return jsonify(message.to_dict())
