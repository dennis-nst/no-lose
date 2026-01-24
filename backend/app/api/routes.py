from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.services.whatsapp import whatsapp_service
from app.models.whatsapp import Message, Contact, Conversation

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@router.get("/whatsapp/verify")
async def verify_whatsapp_token():
    """Verify that the WhatsApp access token is valid"""
    try:
        result = await whatsapp_service.verify_token()
        return {"status": "ok", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/whatsapp/profile")
async def get_business_profile():
    """Get WhatsApp Business Profile"""
    try:
        result = await whatsapp_service.get_business_profile()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/whatsapp/phone-numbers")
async def get_phone_numbers():
    """Get all phone numbers associated with the business account"""
    try:
        result = await whatsapp_service.get_phone_numbers()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/whatsapp/templates")
async def get_message_templates():
    """Get all message templates"""
    try:
        result = await whatsapp_service.get_message_templates()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Webhook endpoints for receiving messages
@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """Webhook verification endpoint for WhatsApp"""
    if hub_mode == "subscribe" and hub_verify_token == settings.wa_verify_token:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def receive_webhook(request: Request, db: Session = Depends(get_db)):
    """Receive incoming WhatsApp messages"""
    try:
        data = await request.json()

        # Process and save the message
        message = whatsapp_service.save_incoming_message(db, data)

        if message:
            return {"status": "ok", "message_id": message.id}
        return {"status": "ok", "message": "No message to process"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Data endpoints
@router.get("/messages")
async def get_messages(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    contact_id: Optional[int] = None
):
    """Get all saved messages"""
    query = db.query(Message)
    if contact_id:
        query = query.filter(Message.contact_id == contact_id)
    messages = query.order_by(Message.timestamp.desc()).offset(skip).limit(limit).all()
    return {"messages": [
        {
            "id": m.id,
            "wa_message_id": m.wa_message_id,
            "type": m.message_type,
            "content": m.content,
            "is_outbound": m.is_outbound,
            "timestamp": m.timestamp.isoformat() if m.timestamp else None,
            "contact_id": m.contact_id
        } for m in messages
    ]}


@router.get("/contacts")
async def get_contacts(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """Get all contacts"""
    contacts = db.query(Contact).offset(skip).limit(limit).all()
    return {"contacts": [
        {
            "id": c.id,
            "wa_id": c.wa_id,
            "name": c.name,
            "profile_name": c.profile_name,
            "created_at": c.created_at.isoformat()
        } for c in contacts
    ]}


@router.get("/conversations")
async def get_conversations(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """Get all conversations"""
    conversations = db.query(Conversation).offset(skip).limit(limit).all()
    return {"conversations": [
        {
            "id": c.id,
            "contact_id": c.contact_id,
            "started_at": c.started_at.isoformat(),
            "last_message_at": c.last_message_at.isoformat() if c.last_message_at else None,
            "is_active": c.is_active
        } for c in conversations
    ]}


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get statistics about stored data"""
    return {
        "total_messages": db.query(Message).count(),
        "total_contacts": db.query(Contact).count(),
        "total_conversations": db.query(Conversation).count(),
        "inbound_messages": db.query(Message).filter(Message.is_outbound == False).count(),
        "outbound_messages": db.query(Message).filter(Message.is_outbound == True).count()
    }
