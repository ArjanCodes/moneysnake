class MoneybirdError(Exception):
    """Base exception for all Moneysnake errors."""


class MoneybirdAPIError(MoneybirdError):
    """Raised when the Moneybird API returns an error response."""

    def __init__(
        self,
        status_code: int,
        response_body: str,
        method: str,
        path: str,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        self.method = method
        self.path = path
        super().__init__(
            f"{method.upper()} {path} returned {status_code}: {response_body}"
        )


class MoneybirdNotFoundError(MoneybirdAPIError):
    """Raised when the requested resource is not found (404)."""


class MoneybirdValidationError(MoneybirdAPIError):
    """Raised when the API rejects the request due to validation errors (422)."""


class MoneybirdRateLimitError(MoneybirdAPIError):
    """Raised when the API rate limit is exceeded (429)."""
