"""HoldCaptureDestinationInvalid application error."""

from __future__ import annotations

from application.errors.base import InvalidOperationError


class HoldCaptureDestinationInvalid(InvalidOperationError):
    """The capture destination is invalid."""

    error_code = "HOLD_CAPTURE_DESTINATION_INVALID"
    public_message = "The destination account is invalid for a full hold capture."
