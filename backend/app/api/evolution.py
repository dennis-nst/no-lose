"""
Evolution API Routes

Endpoints for WhatsApp connection via Evolution API,
including instance management, contact/message sync, and messaging.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.evolution import EvolutionInstance
from app.models.whatsapp import Contact, Message
from app.services.evolution import evolution_service, EvolutionAPIError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evolution", tags=["evolution"])


# ==================== Pydantic Schemas ====================

class InstanceStatusResponse(BaseModel):
    instance_name: str
    status: str
    phone_number: Optional[str] = None
    profile_name: Optional[str] = None
    qr_code: Optional[str] = None
    last_connected_at: Optional[str] = None


class QRCodeResponse(BaseModel):
    qr_code: str
    instance_name: str


class SyncResult(BaseModel):
    synced_count: int
    message: str


class SendTextRequest(BaseModel):
    phone_number: str
    text: str


class SendTextResponse(BaseModel):
    success: bool
    message_id: Optional[str] = None


class ChatInfo(BaseModel):
    id: str
    name: Optional[str] = None
    unread_count: int = 0
    last_message_time: Optional[str] = None


class ContactInfo(BaseModel):
    id: int
    wa_id: str
    name: Optional[str] = None
    profile_name: Optional[str] = None
    evolution_remote_jid: Optional[str] = None


# ==================== Helper Functions ====================

def get_user_instance_name(user_id: int) -> str:
    """Generate instance name for user."""
    return f"user_{user_id}"


async def get_or_create_instance(
    db: Session,
    user: User
) -> EvolutionInstance:
    """Get existing instance or create a new one."""
    instance = db.query(EvolutionInstance).filter(
        EvolutionInstance.user_id == user.id
    ).first()

    if not instance:
        instance = EvolutionInstance(
            user_id=user.id,
            instance_name=get_user_instance_name(user.id),
            status="disconnected"
        )
        db.add(instance)
        db.commit()
        db.refresh(instance)

    return instance


# ==================== Instance Management ====================

@router.post("/instance/create", response_model=InstanceStatusResponse)
async def create_instance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create Evolution API instance for current user and get QR code.

    If instance already exists, returns current status.
    If instance is disconnected, triggers QR code generation.
    """
    instance = await get_or_create_instance(db, current_user)

    try:
        # Try to get current status first
        try:
            status_response = await evolution_service.get_instance_status(instance.instance_name)
            state = status_response.get("state", "close")

            if state == "open":
                instance.status = "connected"
                db.commit()
                return InstanceStatusResponse(
                    instance_name=instance.instance_name,
                    status="connected",
                    phone_number=instance.phone_number,
                    profile_name=instance.profile_name,
                    last_connected_at=instance.last_connected_at.isoformat() if instance.last_connected_at else None
                )
        except EvolutionAPIError:
            # Instance doesn't exist in Evolution, we'll create it
            pass

        # Create new instance (QR typically not in create response for v2)
        try:
            await evolution_service.create_instance(instance.instance_name)
        except EvolutionAPIError as e:
            # 403 = instance already exists, that's fine
            if e.status_code != 403:
                raise

        # Get QR code via connect endpoint (reliable in Evolution API v2)
        await asyncio.sleep(1)  # Brief pause for instance initialization

        qr_code = None
        try:
            connect_response = await evolution_service.connect_instance(instance.instance_name)
            qr_code = connect_response.get("base64")
        except EvolutionAPIError:
            logger.warning(f"Failed to get QR from connect for {instance.instance_name}")

        instance.status = "qr" if qr_code else "connecting"
        instance.qr_code = qr_code
        instance.qr_code_updated_at = datetime.utcnow() if qr_code else None
        db.commit()

        return InstanceStatusResponse(
            instance_name=instance.instance_name,
            status=instance.status,
            qr_code=qr_code
        )

    except EvolutionAPIError as e:
        logger.error(f"Evolution API error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evolution API error: {e.message}"
        )


@router.get("/instance/status", response_model=InstanceStatusResponse)
async def get_instance_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current connection status for user's WhatsApp instance.

    This endpoint only checks connectionState — it does NOT generate new QR codes.
    The cached QR from the DB is returned if still in "qr" state.
    """
    instance = db.query(EvolutionInstance).filter(
        EvolutionInstance.user_id == current_user.id
    ).first()

    if not instance:
        return InstanceStatusResponse(
            instance_name=get_user_instance_name(current_user.id),
            status="disconnected"
        )

    try:
        status_response = await evolution_service.get_instance_status(instance.instance_name)
        state = status_response.get("state", "close")

        # Map Evolution states to our states
        if state == "open":
            instance.status = "connected"
            instance.last_connected_at = datetime.utcnow()
            instance.qr_code = None
        elif state == "connecting":
            # Instance exists and is waiting for QR scan.
            # Return "connecting" so frontend knows polling should continue.
            # Don't return cached QR — frontend fetches fresh QR separately.
            instance.status = "connecting"
        else:
            # close / unknown = disconnected
            instance.status = "disconnected"
            instance.qr_code = None

        db.commit()

        return InstanceStatusResponse(
            instance_name=instance.instance_name,
            status=instance.status,
            phone_number=instance.phone_number,
            profile_name=instance.profile_name,
            qr_code=instance.qr_code if instance.status == "qr" else None,
            last_connected_at=instance.last_connected_at.isoformat() if instance.last_connected_at else None
        )

    except EvolutionAPIError as e:
        # Instance might not exist in Evolution
        return InstanceStatusResponse(
            instance_name=instance.instance_name,
            status="disconnected"
        )


@router.get("/instance/qrcode", response_model=QRCodeResponse)
async def get_qrcode(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get or refresh QR code for WhatsApp connection."""
    instance = db.query(EvolutionInstance).filter(
        EvolutionInstance.user_id == current_user.id
    ).first()

    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found. Create one first."
        )

    try:
        # First check if already connected
        try:
            status_response = await evolution_service.get_instance_status(instance.instance_name)
            if status_response.get("state") == "open":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Instance is already connected. No QR code needed."
                )
        except EvolutionAPIError:
            pass

        # Get QR via connect endpoint (reliable in Evolution API v2)
        qr_response = await evolution_service.get_instance_qrcode(instance.instance_name)
        qr_code = qr_response.get("base64")

        if not qr_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="QR code not available. Try creating a new instance."
            )

        instance.qr_code = qr_code
        instance.qr_code_updated_at = datetime.utcnow()
        instance.status = "qr"
        db.commit()

        return QRCodeResponse(
            qr_code=qr_code,
            instance_name=instance.instance_name
        )

    except HTTPException:
        raise
    except EvolutionAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get QR code: {e.message}"
        )


@router.delete("/instance/disconnect")
async def disconnect_instance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect WhatsApp instance (logout and delete from Evolution)."""
    instance = db.query(EvolutionInstance).filter(
        EvolutionInstance.user_id == current_user.id
    ).first()

    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found"
        )

    try:
        # Try logout first, then delete to clean up fully
        try:
            await evolution_service.logout_instance(instance.instance_name)
        except EvolutionAPIError:
            pass
        try:
            await evolution_service.delete_instance(instance.instance_name)
        except EvolutionAPIError:
            pass

        instance.status = "disconnected"
        instance.qr_code = None
        db.commit()

        return {"message": "Successfully disconnected"}

    except Exception as e:
        logger.error(f"Disconnect error: {e}")
        # Still reset local status even if Evolution API fails
        instance.status = "disconnected"
        instance.qr_code = None
        db.commit()
        return {"message": "Disconnected (with warnings)"}


# ==================== Sync Operations ====================

@router.post("/sync/contacts", response_model=SyncResult)
async def sync_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Synchronize all contacts from WhatsApp."""
    instance = db.query(EvolutionInstance).filter(
        EvolutionInstance.user_id == current_user.id
    ).first()

    if not instance or instance.status != "connected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WhatsApp not connected. Please scan QR code first."
        )

    try:
        contacts = await evolution_service.fetch_contacts(instance.instance_name)
        synced_count = 0

        for contact_data in contacts:
            # Skip group chats
            remote_jid = contact_data.get("id", contact_data.get("remoteJid", ""))
            if "@g.us" in remote_jid:
                continue

            evolution_service.sync_contact_to_db(db, contact_data, current_user.id)
            synced_count += 1

        return SyncResult(
            synced_count=synced_count,
            message=f"Successfully synced {synced_count} contacts"
        )

    except EvolutionAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync contacts: {e.message}"
        )


@router.post("/sync/chats")
async def sync_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of available chats from WhatsApp."""
    instance = db.query(EvolutionInstance).filter(
        EvolutionInstance.user_id == current_user.id
    ).first()

    if not instance or instance.status != "connected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WhatsApp not connected. Please scan QR code first."
        )

    try:
        chats = await evolution_service.fetch_chats(instance.instance_name)

        # Format chats for response
        chat_list = []
        for chat in chats:
            remote_jid = chat.get("id", chat.get("remoteJid", ""))

            # Skip groups for now
            if "@g.us" in remote_jid:
                continue

            chat_list.append({
                "id": remote_jid,
                "name": chat.get("name") or chat.get("pushName"),
                "unread_count": chat.get("unreadCount", 0),
                "last_message_time": chat.get("lastMessageTime")
            })

        return {"chats": chat_list, "total": len(chat_list)}

    except EvolutionAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch chats: {e.message}"
        )


@router.post("/sync/messages/{contact_id}", response_model=SyncResult)
async def sync_messages(
    contact_id: int,
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync message history for a specific contact.

    Args:
        contact_id: Contact ID in our database
        limit: Maximum messages to sync (default: 30)
    """
    instance = db.query(EvolutionInstance).filter(
        EvolutionInstance.user_id == current_user.id
    ).first()

    if not instance or instance.status != "connected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WhatsApp not connected. Please scan QR code first."
        )

    # Get contact
    contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.user_id == current_user.id
    ).first()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    if not contact.evolution_remote_jid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact has no Evolution remote JID. Sync contacts first."
        )

    try:
        messages = await evolution_service.fetch_messages(
            instance.instance_name,
            contact.evolution_remote_jid,
            limit=limit
        )

        synced_count = evolution_service.sync_chat_history(
            db, messages, current_user.id, contact_id
        )

        return SyncResult(
            synced_count=synced_count,
            message=f"Successfully synced {synced_count} new messages"
        )

    except EvolutionAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync messages: {e.message}"
        )


# ==================== Messaging ====================

@router.post("/send/text", response_model=SendTextResponse)
async def send_text_message(
    request: SendTextRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a text message via WhatsApp."""
    instance = db.query(EvolutionInstance).filter(
        EvolutionInstance.user_id == current_user.id
    ).first()

    if not instance or instance.status != "connected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WhatsApp not connected. Please scan QR code first."
        )

    try:
        response = await evolution_service.send_text_message(
            instance.instance_name,
            request.phone_number,
            request.text
        )

        message_id = response.get("key", {}).get("id")

        return SendTextResponse(
            success=True,
            message_id=message_id
        )

    except EvolutionAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {e.message}"
        )


# ==================== Data Endpoints ====================

@router.get("/contacts")
async def get_user_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get contacts for current user."""
    contacts = db.query(Contact).filter(
        Contact.user_id == current_user.id
    ).offset(skip).limit(limit).all()

    return {
        "contacts": [
            ContactInfo(
                id=c.id,
                wa_id=c.wa_id,
                name=c.name,
                profile_name=c.profile_name,
                evolution_remote_jid=c.evolution_remote_jid
            ) for c in contacts
        ],
        "total": len(contacts)
    }


@router.get("/messages/{contact_id}")
async def get_contact_messages(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """Get messages for a specific contact."""
    # Verify contact belongs to user
    contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.user_id == current_user.id
    ).first()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    messages = db.query(Message).filter(
        Message.contact_id == contact_id,
        Message.user_id == current_user.id
    ).order_by(Message.timestamp.desc()).offset(skip).limit(limit).all()

    return {
        "messages": [
            {
                "id": m.id,
                "type": m.message_type,
                "content": m.content,
                "is_outbound": m.is_outbound,
                "status": m.status,
                "timestamp": m.timestamp.isoformat() if m.timestamp else None,
                "source": m.source
            } for m in messages
        ],
        "contact": ContactInfo(
            id=contact.id,
            wa_id=contact.wa_id,
            name=contact.name,
            profile_name=contact.profile_name,
            evolution_remote_jid=contact.evolution_remote_jid
        )
    }
