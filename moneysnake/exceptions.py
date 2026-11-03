import json
from typing import Any


class MoneybirdError(Exception):
    """Base exception for all Moneysnake errors."""


class MoneybirdTransientError(MoneybirdError):
    """Base for failures that may succeed when the request is repeated later."""


class MoneybirdPermanentError(MoneybirdError):
    """Base for failures that will fail again when the same request is repeated."""


def _parse_body(response_body: str) -> dict[str, Any]:
    try:
        body = json.loads(response_body)
    except ValueError:
        return {}
    return body if isinstance(body, dict) else {}


class MoneybirdAPIError(MoneybirdError):
    """Raised when the Moneybird API returns an error response."""

    def __init__(
        self,
        status_code: int,
        response_body: str,
        method: str,
        path: str,
        *,
        retry_after: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        self.method = method
        self.path = path
        self.retry_after = retry_after
        self._body = _parse_body(response_body)
        super().__init__(
            f"{method.upper()} {path} returned {status_code}: {response_body}"
        )

    @property
    def body(self) -> dict[str, Any]:
        """The parsed JSON error body, or an empty dict when it is not a JSON object."""
        return self._body

    @property
    def message(self) -> str:
        """The full message, the error string, or the raw body text."""
        for key in ("full_message", "error"):
            value = self._body.get(key)
            if isinstance(value, str):
                return value
        return self.response_body

    @property
    def field_errors(self) -> dict[str, list[str]]:
        """Messages per rejected field, empty when the body has no field mapping."""
        errors = self._body.get("error")
        if not isinstance(errors, dict):
            return {}
        return {
            field: [str(message) for message in messages]
            for field, messages in errors.items()
            if isinstance(messages, list)
        }

    @property
    def field_error_codes(self) -> dict[str, list[str]]:
        """Error codes per rejected field, taken from the details mapping."""
        details = self._body.get("details")
        if not isinstance(details, dict):
            return {}
        return {
            field: [
                str(item["error"])
                for item in items
                if isinstance(item, dict) and "error" in item
            ]
            for field, items in details.items()
            if isinstance(items, list)
        }

    @property
    def symbolic(self) -> dict[str, Any] | None:
        """The nested mapping of symbolic error codes, when the body has one."""
        symbolic = self._body.get("symbolic")
        return symbolic if isinstance(symbolic, dict) else None


class MoneybirdBadRequestError(MoneybirdAPIError, MoneybirdPermanentError):
    """Raised when the request is malformed (400)."""


class MoneybirdAuthenticationError(MoneybirdAPIError, MoneybirdPermanentError):
    """Raised when the token is missing or invalid (401)."""


class MoneybirdPaymentRequiredError(MoneybirdAPIError, MoneybirdPermanentError):
    """Raised when the administration's subscription does not allow the request (402)."""


class MoneybirdForbiddenError(MoneybirdAPIError, MoneybirdPermanentError):
    """Raised when the token has no access to the resource (403)."""


class MoneybirdNotFoundError(MoneybirdAPIError, MoneybirdPermanentError):
    """Raised when the requested resource is not found (404)."""


class MoneybirdValidationError(MoneybirdAPIError, MoneybirdPermanentError):
    """Raised when the API rejects the request due to validation errors (422)."""


class MoneybirdClientError(MoneybirdAPIError, MoneybirdPermanentError):
    """Raised for any other 4xx response that has no more specific class."""


class MoneybirdRateLimitError(MoneybirdAPIError, MoneybirdTransientError):
    """Raised when the API rate limit is exceeded (429)."""


class MoneybirdServerError(MoneybirdAPIError, MoneybirdTransientError):
    """Raised when the API fails on its side (5xx)."""


class MoneybirdConnectionError(MoneybirdTransientError):
    """Raised when the request got no response, for example a timeout or a refused connection."""

    def __init__(self, method: str, path: str, reason: str) -> None:
        self.method = method
        self.path = path
        super().__init__(f"{method.upper()} {path} failed: {reason}")
