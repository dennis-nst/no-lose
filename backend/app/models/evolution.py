from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class EvolutionInstance(Base):
    """Model for tracking WhatsApp Evolution API instances per user."""
    __tablename__ = "evolution_instances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # Instance identification
    instance_name = Column(String(100), unique=True, index=True)  # Format: user_{user_id}

    # Connection status: disconnected, qr, connecting, connected
    status = Column(String(50), default="disconnected")

    # QR Code data
    qr_code = Column(Text, nullable=True)  # Base64 encoded QR code
    qr_code_updated_at = Column(DateTime, nullable=True)

    # Profile info (populated after connection)
    phone_number = Column(String(50), nullable=True)
    profile_name = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_connected_at = Column(DateTime, nullable=True)

    # Raw API response data
    raw_data = Column(JSON, nullable=True)

    # Relationship to user
    user = relationship("User", back_populates="evolution_instance")
