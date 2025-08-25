"""Pub/Sub functionality for AlphaLoop Cache."""

import asyncio
import json
from collections.abc import Callable
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from ..exceptions import PubSubError
from ..utils.key_builder import KeyBuilder
from .connection import CacheManager


class PubSubMessage(BaseModel):
    """Pub/Sub message model."""

    channel: str
    message: dict[str, Any]
    timestamp: datetime
    message_id: str | None = None
    sender: str | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "channel": self.channel,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "message_id": self.message_id,
            "sender": self.sender,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PubSubMessage":
        """Create from dictionary."""
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class MessageHandler:
    """Message handler for pub/sub."""

    def __init__(self, callback: Callable[[PubSubMessage], Any]) -> None:
        """Initialize message handler."""
        self.callback = callback
        self.is_active = True

    async def handle(self, message: PubSubMessage) -> None:
        """Handle incoming message."""
        if self.is_active:
            try:
                if asyncio.iscoroutinefunction(self.callback):
                    await self.callback(message)
                else:
                    self.callback(message)
            except Exception as e:
                print(f"Error in message handler: {e}")


class PubSubManager:
    """Manages pub/sub operations for cloud messaging."""

    def __init__(
        self,
        cache_manager: CacheManager,
        default_ttl: int = 3600,  # 1 hour for pub/sub messages
    ) -> None:
        """Initialize pub/sub manager."""
        self.cache_manager = cache_manager
        self.default_ttl = default_ttl
        self.key_builder = KeyBuilder(prefix="pubsub")
        self._handlers: dict[str, list[MessageHandler]] = {}
        self._subscribers: dict[str, Any] = {}
        self._is_running = False

    async def publish(
        self,
        channel: str,
        message: dict[str, Any],
        message_id: str | None = None,
        sender: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Publish message to channel."""
        try:
            pubsub_message = PubSubMessage(
                channel=channel,
                message=message,
                timestamp=datetime.utcnow(),
                message_id=message_id,
                sender=sender,
                metadata=metadata or {},
            )

            # Store message in cache
            key = self.key_builder.build_message_key(channel, pubsub_message.timestamp)
            await self.cache_manager.set_key(key, pubsub_message.to_dict(), ttl=self.default_ttl)

            # Publish to Redis pub/sub
            await self.cache_manager.redis_client.publish(
                channel, json.dumps(pubsub_message.to_dict())
            )

            return True
        except Exception as e:
            raise PubSubError(f"Failed to publish message to {channel}: {e}") from e

    async def subscribe(self, channel: str, handler: Callable[[PubSubMessage], Any]) -> str:
        """Subscribe to channel with handler."""
        try:
            if channel not in self._handlers:
                self._handlers[channel] = []

            message_handler = MessageHandler(handler)
            self._handlers[channel].append(message_handler)

            # Create Redis pubsub subscriber
            if channel not in self._subscribers:
                pubsub = self.cache_manager.redis_client.pubsub()
                await pubsub.subscribe(channel)
                self._subscribers[channel] = pubsub

            return f"subscriber_{len(self._handlers[channel])}"
        except Exception as e:
            raise PubSubError(f"Failed to subscribe to {channel}: {e}") from e

    async def unsubscribe(self, channel: str, handler_id: str | None = None) -> bool:
        """Unsubscribe from channel."""
        try:
            if channel not in self._handlers:
                return False

            if handler_id:
                # Remove specific handler
                handlers = self._handlers[channel]
                for i, handler in enumerate(handlers):
                    if f"subscriber_{i+1}" == handler_id:
                        handler.is_active = False
                        handlers.pop(i)
                        break
            else:
                # Remove all handlers
                for handler in self._handlers[channel]:
                    handler.is_active = False
                self._handlers[channel].clear()

            # Unsubscribe from Redis if no more handlers
            if not self._handlers[channel]:
                if channel in self._subscribers:
                    await self._subscribers[channel].unsubscribe(channel)
                    await self._subscribers[channel].close()
                    del self._subscribers[channel]
                del self._handlers[channel]

            return True
        except Exception as e:
            raise PubSubError(f"Failed to unsubscribe from {channel}: {e}") from e

    async def start_listening(self) -> None:
        """Start listening for messages."""
        if self._is_running:
            return

        self._is_running = True
        try:
            while self._is_running and self._subscribers:
                for channel, pubsub in self._subscribers.items():
                    try:
                        message = await pubsub.get_message(timeout=1.0)
                        if message and message["type"] == "message":
                            await self._handle_message(channel, message["data"])
                    except Exception as e:
                        print(f"Error processing message from {channel}: {e}")

                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
        except Exception as e:
            raise PubSubError(f"Error in message listening: {e}") from e

    async def stop_listening(self) -> None:
        """Stop listening for messages."""
        self._is_running = False

        # Close all subscribers
        for channel, pubsub in self._subscribers.items():
            try:
                await pubsub.unsubscribe(channel)
                await pubsub.close()
            except Exception as e:
                print(f"Error closing subscriber for {channel}: {e}")

        self._subscribers.clear()
        self._handlers.clear()

    async def _handle_message(self, channel: str, data: bytes) -> None:
        """Handle incoming message."""
        try:
            message_data = json.loads(data.decode("utf-8"))
            pubsub_message = PubSubMessage.from_dict(message_data)

            if channel in self._handlers:
                for handler in self._handlers[channel]:
                    if handler.is_active:
                        await handler.handle(pubsub_message)
        except Exception as e:
            print(f"Error handling message from {channel}: {e}")

    async def get_channel_messages(self, channel: str, limit: int = 100) -> list[PubSubMessage]:
        """Get recent messages from channel."""
        try:
            pattern = self.key_builder.build_channel_pattern(channel)
            keys = await self._get_keys_by_pattern(pattern)

            messages = []
            for key in keys:
                cached_data = await self.cache_manager.get_key(key)
                if cached_data:
                    try:
                        message = PubSubMessage.from_dict(cached_data)
                        messages.append(message)
                    except Exception as e:
                        print(f"Error parsing message from {key}: {e}")

            # Sort by timestamp (newest first)
            messages.sort(key=lambda x: x.timestamp, reverse=True)
            return messages[:limit]
        except Exception as e:
            raise PubSubError(f"Failed to get messages from {channel}: {e}") from e

    async def get_active_channels(self) -> list[str]:
        """Get list of active channels."""
        try:
            return list(self._handlers.keys())
        except Exception as e:
            raise PubSubError(f"Failed to get active channels: {e}") from e

    async def get_channel_stats(self, channel: str) -> dict[str, Any]:
        """Get statistics for a channel."""
        try:
            pattern = self.key_builder.build_channel_pattern(channel)
            keys = await self._get_keys_by_pattern(pattern)

            # Get recent messages
            recent_messages = await self.get_channel_messages(channel, limit=10)

            return {
                "channel": channel,
                "total_messages": len(keys),
                "recent_messages": len(recent_messages),
                "subscribers": len(self._handlers.get(channel, [])),
                "last_message": recent_messages[0].timestamp if recent_messages else None,
            }
        except Exception as e:
            raise PubSubError(f"Failed to get stats for {channel}: {e}") from e

    async def _get_keys_by_pattern(self, pattern: str) -> list[str]:
        """Get keys matching pattern."""
        try:
            keys = []
            cursor = 0
            while True:
                cursor, batch = await self.cache_manager.redis_client.scan(
                    cursor=cursor, match=pattern, count=100
                )
                keys.extend(batch)
                if cursor == 0:
                    break
            return keys
        except Exception as e:
            raise PubSubError(f"Failed to get keys by pattern: {e}") from e

    async def cleanup_old_messages(self, hours: int = 24) -> int:
        """Clean up old messages."""
        try:
            from datetime import timedelta

            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            pattern = "pubsub:*"
            keys = await self._get_keys_by_pattern(pattern)

            cleaned_count = 0
            for key in keys:
                cached_data = await self.cache_manager.get_key(key)
                if cached_data:
                    try:
                        message = PubSubMessage.from_dict(cached_data)
                        if message.timestamp < cutoff_time:
                            if await self.cache_manager.delete_key(key):
                                cleaned_count += 1
                    except Exception:
                        # If we can't parse the message, delete it
                        if await self.cache_manager.delete_key(key):
                            cleaned_count += 1

            return cleaned_count
        except Exception as e:
            raise PubSubError(f"Failed to cleanup old messages: {e}") from e
