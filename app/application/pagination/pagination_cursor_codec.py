"""Opaque structural keyset cursor codec."""

from __future__ import annotations

import base64
import binascii
from datetime import datetime
from uuid import UUID

from application.errors import HistoryCursorInvalid

from .pagination_cursor import PaginationCursor
from .pagination_input import CURSOR_MAX_LENGTH


class PaginationCursorCodec:
    """Encode and decode a UTC timestamp plus UUID cursor."""

    def encode(self, cursor: PaginationCursor) -> str:
        """Serialize an internal keyset into an opaque URL-safe token."""
        payload = f"{cursor.occurred_at.isoformat()}|{cursor.item_id}".encode("ascii")
        return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")

    def decode(self, value: str | None) -> PaginationCursor | None:
        """Validate bounded canonical base64 and return a typed keyset."""
        if value is None:
            return None
        if not value or len(value) > CURSOR_MAX_LENGTH:
            raise HistoryCursorInvalid()
        padding = "=" * (-len(value) % 4)
        try:
            decoded = base64.b64decode(
                value + padding,
                altchars=b"-_",
                validate=True,
            ).decode("ascii")
            timestamp_value, item_id_value = decoded.split("|", maxsplit=1)
            cursor = PaginationCursor(
                occurred_at=datetime.fromisoformat(timestamp_value),
                item_id=UUID(item_id_value),
            )
        except (binascii.Error, UnicodeDecodeError, ValueError) as exception:
            raise HistoryCursorInvalid() from exception
        if self.encode(cursor) != value:
            raise HistoryCursorInvalid()
        return cursor
