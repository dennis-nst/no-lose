from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Owner of this contact
    wa_id = Column(String(50), index=True)  # WhatsApp ID (phone number)
    name = Column(String(255), nullable=True)
    profile_name = Column(String(255), nullable=True)

    # Evolution API specific fields
    evolution_remote_jid = Column(String(100), nullable=True, index=True)  # e.g., 1234567890@s.whatsapp.net

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("Message", back_populates="contact")
    conversations = relationship("Conversation", back_populates="contact")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    contact = relationship("Contact", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Owner of this message
    wa_message_id = Column(String(255), index=True)  # Cloud API message ID
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)

    # Evolution API specific fields
    evolution_key_id = Column(String(255), nullable=True, unique=True, index=True)  # Evolution message key
    source = Column(String(50), default="cloud_api")  # cloud_api | evolution_api

    # Message content
    message_type = Column(String(50))  # text, image, video, audio, document, etc.
    content = Column(Text, nullable=True)  # Text content or media caption
    media_url = Column(String(500), nullable=True)
    media_id = Column(String(255), nullable=True)

    # Direction
    is_outbound = Column(Boolean, default=False)  # True if sent by us, False if received

    # Status
    status = Column(String(50), default="received")  # sent, delivered, read, failed

    # Timestamps
    timestamp = Column(DateTime)  # Original message timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Raw data for debugging
    raw_data = Column(JSON, nullable=True)

    contact = relationship("Contact", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")
