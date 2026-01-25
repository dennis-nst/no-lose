"""
Evolution API Service Layer

Handles all interactions with Evolution API for WhatsApp messaging.
Includes instance management, message fetching, and database synchronization.
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.evolution import EvolutionInstance
from app.models.whatsapp import Contact, Message, Conversation

logger = logging.getLogger(__name__)


class EvolutionAPIError(Exception):
    """Custom exception for Evolution API errors."""
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class EvolutionAPIService:
    """Service class for interacting with Evolution API."""

    def __init__(self):
        self.base_url = settings.evolution_api_url
        self.api_key = settings.evolution_api_key
        self.timeout = 30.0

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: dict = None,
        params: dict = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Evolution API."""
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self._get_headers(),
                    json=data,
                    params=params
                )

                if response.status_code >= 400:
                    error_data = response.json() if response.content else {}
                    raise EvolutionAPIError(
                        message=f"Evolution API error: {response.status_code}",
                        status_code=response.status_code,
                        response_data=error_data
                    )

                return response.json() if response.content else {}

            except httpx.RequestError as e:
                logger.error(f"Evolution API request error: {e}")
                raise EvolutionAPIError(f"Connection error: {str(e)}")

    # ==================== Instance Management ====================

    async def create_instance(self, instance_name: str) -> Dict[str, Any]:
        """
        Create a new Evolution API instance.

        POST /instance/create
        """
        data = {
            "instanceName": instance_name,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        return await self._make_request("POST", "/instance/create", data=data)

    async def connect_instance(self, instance_name: str) -> Dict[str, Any]:
        """
        Connect an existing instance (triggers QR code generation).

        POST /instance/connect/{name}
        """
        return await self._make_request("POST", f"/instance/connect/{instance_name}")

    async def get_instance_status(self, instance_name: str) -> Dict[str, Any]:
        """
        Get connection state of an instance.

        GET /instance/connectionState/{name}
        Returns: { "instance": {...}, "state": "open"|"close"|"connecting" }
        """
        return await self._make_request("GET", f"/instance/connectionState/{instance_name}")

    async def get_instance_qrcode(self, instance_name: str) -> Dict[str, Any]:
        """
        Get QR code for an instance.

        GET /instance/qrcode/{name}
        Returns: { "pairingCode": null, "code": "2@...", "base64": "data:image/png;base64,..." }
        """
        return await self._make_request("GET", f"/instance/qrcode/{instance_name}")

    async def logout_instance(self, instance_name: str) -> Dict[str, Any]:
        """
        Logout from WhatsApp (disconnect).

        DELETE /instance/logout/{name}
        """
        return await self._make_request("DELETE", f"/instance/logout/{instance_name}")

    async def delete_instance(self, instance_name: str) -> Dict[str, Any]:
        """
        Delete an instance completely.

        DELETE /instance/delete/{name}
        """
        return await self._make_request("DELETE", f"/instance/delete/{instance_name}")

    async def fetch_instances(self) -> List[Dict[str, Any]]:
        """
        Fetch all instances.

        GET /instance/fetchInstances
        """
        return await self._make_request("GET", "/instance/fetchInstances")

    # ==================== Data Fetching ====================

    async def fetch_contacts(self, instance_name: str) -> List[Dict[str, Any]]:
        """
        Fetch all contacts from WhatsApp.

        GET /chat/findContacts/{name}
        """
        result = await self._make_request("GET", f"/chat/findContacts/{instance_name}")
        return result if isinstance(result, list) else result.get("contacts", [])

    async def fetch_chats(self, instance_name: str) -> List[Dict[str, Any]]:
        """
        Fetch all chats from WhatsApp.

        GET /chat/findChats/{name}
        """
        result = await self._make_request("GET", f"/chat/findChats/{instance_name}")
        return result if isinstance(result, list) else result.get("chats", [])

    async def fetch_messages(
        self,
        instance_name: str,
        remote_jid: str,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Fetch message history for a specific chat.

        POST /chat/findMessages/{name}

        Args:
            instance_name: The Evolution instance name
            remote_jid: The WhatsApp JID (e.g., 1234567890@s.whatsapp.net)
            limit: Maximum number of messages to fetch (default: 30)
        """
        data = {
            "where": {
                "key": {
                    "remoteJid": remote_jid
                }
            },
            "limit": limit
        }
        result = await self._make_request("POST", f"/chat/findMessages/{instance_name}", data=data)
        return result if isinstance(result, list) else result.get("messages", [])

    # ==================== Sending Messages ====================

    async def send_text_message(
        self,
        instance_name: str,
        number: str,
        text: str
    ) -> Dict[str, Any]:
        """
        Send a text message.

        POST /message/sendText/{name}

        Args:
            instance_name: The Evolution instance name
            number: Phone number (without @s.whatsapp.net)
            text: Message text
        """
        data = {
            "number": number,
            "text": text
        }
        return await self._make_request("POST", f"/message/sendText/{instance_name}", data=data)

    async def send_media_message(
        self,
        instance_name: str,
        number: str,
        media_type: str,
        media_url: str,
        caption: str = None
    ) -> Dict[str, Any]:
        """
        Send a media message.

        POST /message/sendMedia/{name}
        """
        data = {
            "number": number,
            "mediatype": media_type,
            "media": media_url,
        }
        if caption:
            data["caption"] = caption

        return await self._make_request("POST", f"/message/sendMedia/{instance_name}", data=data)

    # ==================== Database Sync ====================

    def sync_contact_to_db(
        self,
        db: Session,
        evolution_contact: Dict[str, Any],
        user_id: int
    ) -> Contact:
        """
        Sync a single Evolution contact to database.

        Args:
            db: Database session
            evolution_contact: Contact data from Evolution API
            user_id: Owner user ID

        Returns:
            Contact object (created or updated)
        """
        remote_jid = evolution_contact.get("id", evolution_contact.get("remoteJid", ""))
        # Extract phone number from JID (e.g., "1234567890@s.whatsapp.net" -> "1234567890")
        phone_number = remote_jid.split("@")[0] if "@" in remote_jid else remote_jid

        # Try to find existing contact by remote_jid and user_id
        contact = db.query(Contact).filter(
            Contact.user_id == user_id,
            Contact.evolution_remote_jid == remote_jid
        ).first()

        if not contact:
            # Try to find by phone number
            contact = db.query(Contact).filter(
                Contact.user_id == user_id,
                Contact.wa_id == phone_number
            ).first()

        if contact:
            # Update existing contact
            contact.evolution_remote_jid = remote_jid
            contact.profile_name = evolution_contact.get("pushName", contact.profile_name)
            contact.name = evolution_contact.get("name", contact.name) or contact.profile_name
            contact.updated_at = datetime.utcnow()
        else:
            # Create new contact
            contact = Contact(
                user_id=user_id,
                wa_id=phone_number,
                evolution_remote_jid=remote_jid,
                name=evolution_contact.get("name") or evolution_contact.get("pushName"),
                profile_name=evolution_contact.get("pushName"),
            )
            db.add(contact)

        db.commit()
        db.refresh(contact)
        return contact

    def sync_message_to_db(
        self,
        db: Session,
        evolution_message: Dict[str, Any],
        user_id: int,
        contact_id: int
    ) -> Optional[Message]:
        """
        Sync a single Evolution message to database with deduplication.

        Args:
            db: Database session
            evolution_message: Message data from Evolution API
            user_id: Owner user ID
            contact_id: Contact ID in our database

        Returns:
            Message object or None if duplicate
        """
        # Extract message key for deduplication
        key_data = evolution_message.get("key", {})
        message_key_id = key_data.get("id")

        if not message_key_id:
            logger.warning("Message without key ID, skipping")
            return None

        # Check for duplicate
        existing = db.query(Message).filter(
            Message.evolution_key_id == message_key_id
        ).first()

        if existing:
            logger.debug(f"Duplicate message: {message_key_id}")
            return None

        # Determine message type and content
        message_data = evolution_message.get("message", {})
        message_type = "text"
        content = None
        media_url = None

        if "conversation" in message_data:
            message_type = "text"
            content = message_data["conversation"]
        elif "extendedTextMessage" in message_data:
            message_type = "text"
            content = message_data["extendedTextMessage"].get("text")
        elif "imageMessage" in message_data:
            message_type = "image"
            content = message_data["imageMessage"].get("caption")
            media_url = message_data["imageMessage"].get("url")
        elif "videoMessage" in message_data:
            message_type = "video"
            content = message_data["videoMessage"].get("caption")
            media_url = message_data["videoMessage"].get("url")
        elif "audioMessage" in message_data:
            message_type = "audio"
            media_url = message_data["audioMessage"].get("url")
        elif "documentMessage" in message_data:
            message_type = "document"
            content = message_data["documentMessage"].get("fileName")
            media_url = message_data["documentMessage"].get("url")
        elif "stickerMessage" in message_data:
            message_type = "sticker"
        else:
            # Unknown message type, store raw
            message_type = "unknown"
            content = str(message_data)[:500] if message_data else None

        # Parse timestamp
        timestamp = None
        if "messageTimestamp" in evolution_message:
            ts = evolution_message["messageTimestamp"]
            if isinstance(ts, (int, float)):
                timestamp = datetime.fromtimestamp(ts)

        # Determine direction
        is_outbound = key_data.get("fromMe", False)

        message = Message(
            user_id=user_id,
            contact_id=contact_id,
            evolution_key_id=message_key_id,
            source="evolution_api",
            message_type=message_type,
            content=content,
            media_url=media_url,
            is_outbound=is_outbound,
            status="received" if not is_outbound else "sent",
            timestamp=timestamp or datetime.utcnow(),
            raw_data=evolution_message
        )

        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def sync_chat_history(
        self,
        db: Session,
        messages: List[Dict[str, Any]],
        user_id: int,
        contact_id: int
    ) -> int:
        """
        Sync multiple messages to database.

        Args:
            db: Database session
            messages: List of messages from Evolution API
            user_id: Owner user ID
            contact_id: Contact ID

        Returns:
            Number of new messages synced
        """
        synced_count = 0
        for msg in messages:
            result = self.sync_message_to_db(db, msg, user_id, contact_id)
            if result:
                synced_count += 1

        return synced_count


# Singleton instance
evolution_service = EvolutionAPIService()
