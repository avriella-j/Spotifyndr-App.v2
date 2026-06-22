# app/services/messaging_service.py — Conversation and message logic

from app.models.conversation import Conversation, conversation_participants
from app.models.message import Message
from app.models.user import User
from app.extensions import db
from datetime import datetime


class MessagingService:
    """Messaging logic."""
    
    @staticmethod
    def get_user_conversations(user_id):
        """Get user's conversations."""
        user = User.query.get(user_id)
        return user.conversations if user else []
    
    @staticmethod
    # Find existing or create new conversation between users
    def create_conversation(user_id, participant_id):
        """Create a new conversation."""
        # Check if conversation already exists
        existing_conversations = db.session.query(Conversation).join(
            conversation_participants
        ).filter(
            conversation_participants.c.user_id.in_([user_id, participant_id])
        ).all()
        
        for conv in existing_conversations:
            participants = [p.id for p in conv.participants]
            if set(participants) == {user_id, participant_id}:
                return conv
        
        # Create new conversation
        conversation = Conversation()
        db.session.add(conversation)
        db.session.flush()
        
        # Add participants
        db.session.execute(
            conversation_participants.insert().values(
                conversation_id=conversation.id,
                user_id=user_id
            )
        )
        db.session.execute(
            conversation_participants.insert().values(
                conversation_id=conversation.id,
                user_id=participant_id
            )
        )
        
        db.session.commit()
        return conversation
    
    @staticmethod
    def get_conversation_messages(conversation_id):
        """Get messages from a conversation."""
        return Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()
    
    @staticmethod
    def send_message(sender_id, conversation_id, content):
        """Send a message to a conversation."""
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return None
        
        # Get recipient (the other participant)
        participants = conversation.participants
        recipient = next((p for p in participants if p.id != sender_id), None)
        
        if not recipient:
            return None
        
        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            recipient_id=recipient.id,
            content=content
        )
        
        db.session.add(message)
        conversation.updated_at = datetime.utcnow()
        db.session.commit()
        
        return message
