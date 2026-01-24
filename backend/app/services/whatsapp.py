import httpx
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.whatsapp import Contact, Message, Conversation


class WhatsAppService:
    def __init__(self):
        self.base_url = settings.wa_api_base_url
        self.access_token = settings.wa_access_token
        self.phone_number_id = settings.wa_phone_number_id
        self.business_account_id = settings.wa_business_account_id

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def verify_token(self) -> dict:
        """Verify the access token is valid"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/me",
                headers=self._get_headers()
            )
            return response.json()

    async def get_business_profile(self) -> dict:
        """Get WhatsApp Business Profile info"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{self.phone_number_id}/whatsapp_business_profile",
                headers=self._get_headers(),
                params={"fields": "about,address,description,email,profile_picture_url,websites,vertical"}
            )
            return response.json()

    async def get_phone_numbers(self) -> dict:
        """Get all phone numbers associated with the business account"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{self.business_account_id}/phone_numbers",
                headers=self._get_headers()
            )
            return response.json()

    async def get_message_templates(self) -> dict:
        """Get message templates"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{self.business_account_id}/message_templates",
                headers=self._get_headers()
            )
            return response.json()

    async def download_media(self, media_id: str) -> dict:
        """Get media URL by media ID"""
        async with httpx.AsyncClient() as client:
            # First get the media URL
            response = await client.get(
                f"{self.base_url}/{media_id}",
                headers=self._get_headers()
            )
            media_info = response.json()

            if "url" in media_info:
                # Download the actual media
                media_response = await client.get(
                    media_info["url"],
                    headers=self._get_headers()
                )
                return {
                    "info": media_info,
                    "content_type": media_response.headers.get("content-type"),
                    "size": len(media_response.content)
                }
            return media_info

    async def send_test_message(self, to_phone: str, message: str) -> dict:
        """Send a test text message"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/{self.phone_number_id}/messages",
                headers=self._get_headers(),
                json={
                    "messaging_product": "whatsapp",
                    "to": to_phone,
                    "type": "text",
                    "text": {"body": message}
                }
            )
            return response.json()

    def save_incoming_message(self, db: Session, webhook_data: dict) -> Optional[Message]:
        """Process and save incoming webhook message"""
        try:
            entry = webhook_data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})

            messages = value.get("messages", [])
            contacts = value.get("contacts", [])

            if not messages:
                return None

            msg_data = messages[0]
            contact_data = contacts[0] if contacts else {}

            # Get or create contact
            wa_id = contact_data.get("wa_id") or msg_data.get("from")
            contact = db.query(Contact).filter(Contact.wa_id == wa_id).first()

            if not contact:
                contact = Contact(
                    wa_id=wa_id,
                    profile_name=contact_data.get("profile", {}).get("name")
                )
                db.add(contact)
                db.commit()
                db.refresh(contact)

            # Get or create conversation
            conversation = db.query(Conversation).filter(
                Conversation.contact_id == contact.id,
                Conversation.is_active == True
            ).first()

            if not conversation:
                conversation = Conversation(contact_id=contact.id)
                db.add(conversation)
                db.commit()
                db.refresh(conversation)

            # Create message
            msg_type = msg_data.get("type", "text")
            content = None
            media_id = None

            if msg_type == "text":
                content = msg_data.get("text", {}).get("body")
            elif msg_type in ["image", "video", "audio", "document"]:
                media_info = msg_data.get(msg_type, {})
                media_id = media_info.get("id")
                content = media_info.get("caption")

            message = Message(
                wa_message_id=msg_data.get("id"),
                contact_id=contact.id,
                conversation_id=conversation.id,
                message_type=msg_type,
                content=content,
                media_id=media_id,
                is_outbound=False,
                timestamp=datetime.fromtimestamp(int(msg_data.get("timestamp", 0))),
                raw_data=msg_data
            )
            db.add(message)

            # Update conversation
            conversation.last_message_at = datetime.utcnow()

            db.commit()
            db.refresh(message)

            return message

        except Exception as e:
            db.rollback()
            raise e


whatsapp_service = WhatsAppService()
