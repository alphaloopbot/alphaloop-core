"""Security-related exceptions."""


class SecurityError(Exception):
    """Base exception for security-related errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class UnauthorizedRequestError(SecurityError):
    """Exception raised for unauthorized requests."""

    def __init__(self, message: str = "Authentication error.") -> None:
        super().__init__(message)


class EncryptionError(SecurityError):
    """Exception raised for encryption/decryption errors."""

    def __init__(self, message: str = "Encryption/decryption failed.") -> None:
        super().__init__(message)


class IntegrityError(SecurityError):
    """Exception raised for data integrity violations."""

    def __init__(self, message: str = "Data integrity compromised.") -> None:
        super().__init__(message)
