"""
Authentication utilities for AlphaLoop Security.

This module provides time-based authentication mechanisms for secure communication
between services. The authentication system uses time-based hashing to create
temporary authentication tokens that are valid only for a specific time window.

The authentication system is designed to prevent replay attacks and ensure that
authentication tokens cannot be reused after their time window expires. This is
particularly useful for securing API endpoints and inter-service communication.

Key Features:
- Time-based authentication tokens
- Replay attack prevention
- Configurable time windows
- Secure hash generation
- Cross-platform compatibility
"""

import hashlib
import hmac
import time


class ConnectionAuthenticator:
    """
    Time-based authentication for secure service connections.

    This class provides a secure authentication mechanism based on time-based
    hashing. It generates authentication tokens that are valid only for a
    specific time window, preventing replay attacks and ensuring secure
    communication between services.

    The authenticator uses HMAC-SHA256 with a shared passphrase to generate
    authentication tokens. The tokens are tied to specific time periods,
    making them invalid after their time window expires.

    Key Features:
    - Time-based token generation
    - Replay attack prevention
    - Configurable time windows
    - Secure hash generation
    - Token validation

    Usage:
        authenticator = ConnectionAuthenticator("shared-secret", period_size=300)
        token = authenticator.generate_token()
        is_valid = authenticator.validate_token(token)
    """

    def __init__(
        self,
        passphrase: str,
        period_size: int = 300,
        num_sequential_hashes: int = 2,
    ) -> None:
        """
        Initialize the connection authenticator.

        Creates a new authenticator with the specified configuration. The
        authenticator will generate tokens that are valid for the specified
        time period and use the given number of sequential hashes for
        additional security.

        Args:
            passphrase: Shared secret passphrase for token generation
            period_size: Time window size in seconds (default: 300 = 5 minutes)
            num_sequential_hashes: Number of sequential hash operations for
                                 additional security (default: 2)

        Raises:
            ValueError: If passphrase is empty or period_size is invalid

        Example:
            >>> authenticator = ConnectionAuthenticator("my-secret-key", 300)
            >>> authenticator = ConnectionAuthenticator("shared-passphrase", 600, 3)
        """
        if not passphrase or not passphrase.strip():
            raise ValueError("passphrase cannot be empty")

        if period_size <= 0:
            raise ValueError("period_size must be positive")

        if num_sequential_hashes <= 0:
            raise ValueError("num_sequential_hashes must be positive")

        self.passphrase = passphrase.encode("utf-8")
        self.period_size = period_size
        self.num_sequential_hashes = num_sequential_hashes

    def _get_current_period(self) -> int:
        """
        Get the current time period number.

        Calculates the current time period based on the configured period size.
        This method is used internally to generate time-based tokens.

        Returns:
            Current time period number

        Example:
            >>> authenticator = ConnectionAuthenticator("secret", 300)
            >>> period = authenticator._get_current_period()
            >>> print(period)
            5476800  # Example period number
        """
        return int(time.time() // self.period_size)

    def _generate_hash(self, data: bytes) -> bytes:
        """
        Generate HMAC-SHA256 hash of the given data.

        Creates a secure hash of the provided data using HMAC-SHA256 with
        the configured passphrase as the key. This method is used internally
        for token generation.

        Args:
            data: Data to hash

        Returns:
            HMAC-SHA256 hash as bytes

        Example:
            >>> authenticator = ConnectionAuthenticator("secret")
            >>> hash_bytes = authenticator._generate_hash(b"test-data")
            >>> print(hash_bytes.hex())
            a1b2c3d4e5f6...
        """
        return hmac.new(self.passphrase, data, hashlib.sha256).digest()

    def _apply_sequential_hashes(self, data: bytes) -> bytes:
        """
        Apply multiple sequential hash operations to the data.

        Performs the configured number of sequential hash operations on the
        data. This adds additional security by making it computationally
        more expensive to brute-force the authentication.

        Args:
            data: Initial data to hash

        Returns:
            Data after sequential hash operations

        Example:
            >>> authenticator = ConnectionAuthenticator("secret", num_sequential_hashes=3)
            >>> result = authenticator._apply_sequential_hashes(b"initial-data")
            >>> print(len(result))
            32  # SHA-256 hash length
        """
        result = data
        for _ in range(self.num_sequential_hashes):
            result = self._generate_hash(result)
        return result

    def generate_token(self, custom_period: int | None = None) -> str:
        """
        Generate an authentication token for the current time period.

        Creates a secure authentication token that is valid only for the
        current time window. The token is generated using HMAC-SHA256 with
        the configured passphrase and includes the time period information.

        The token can be used to authenticate requests between services
        that share the same passphrase and configuration.

        Args:
            custom_period: Optional custom time period (for testing or specific use cases)
                          If None, uses the current time period

        Returns:
            Base64-encoded authentication token

        Example:
            >>> authenticator = ConnectionAuthenticator("shared-secret")
            >>> token = authenticator.generate_token()
            >>> print(token)
            eyJwZXJpb2QiOiA1NDc2ODAwLCAiaGFzaCI6ICJhMWIyYzNkNGU1ZjY...}

            >>> # Generate token for a specific period (testing)
            >>> token = authenticator.generate_token(custom_period=12345)
        """
        period = custom_period if custom_period is not None else self._get_current_period()

        # Create period data
        period_data = str(period).encode("utf-8")

        # Generate hash
        hash_result = self._apply_sequential_hashes(period_data)

        # Create token data
        import base64
        import json

        token_data = {
            "period": period,
            "hash": base64.b64encode(hash_result).decode("utf-8"),
        }

        return base64.b64encode(json.dumps(token_data).encode("utf-8")).decode("utf-8")

    def validate_token(self, token: str, tolerance_periods: int = 1) -> bool:
        """
        Validate an authentication token.

        Verifies that the provided token is valid for the current time period
        or within the specified tolerance. The validation checks that the token
        was generated with the correct passphrase and is within the acceptable
        time window.

        Args:
            token: Authentication token to validate
            tolerance_periods: Number of periods to allow for clock skew
                             (default: 1, meaning current period ±1)

        Returns:
            True if the token is valid, False otherwise

        Raises:
            ValueError: If the token format is invalid

        Example:
            >>> authenticator = ConnectionAuthenticator("shared-secret")
            >>> token = authenticator.generate_token()
            >>> is_valid = authenticator.validate_token(token)
            >>> print(f"Token is valid: {is_valid}")
            Token is valid: True

            >>> # Validate with tolerance for clock skew
            >>> is_valid = authenticator.validate_token(token, tolerance_periods=2)
        """
        try:
            import base64
            import json

            # Decode token
            token_bytes = base64.b64decode(token.encode("utf-8"))
            token_data = json.loads(token_bytes.decode("utf-8"))

            # Extract period and hash
            period = token_data.get("period")
            hash_b64 = token_data.get("hash")

            if period is None or hash_b64 is None:
                return False

            # Validate period
            current_period = self._get_current_period()
            if abs(period - current_period) > tolerance_periods:
                return False

            # Validate hash
            expected_hash = self._apply_sequential_hashes(str(period).encode("utf-8"))
            expected_hash_b64 = base64.b64encode(expected_hash).decode("utf-8")

            return hmac.compare_digest(hash_b64, expected_hash_b64)

        except (ValueError, json.JSONDecodeError, KeyError):
            return False

    def get_token_info(self, token: str) -> dict | None:
        """
        Get information about an authentication token.

        Extracts and returns information about the provided token without
        validating it. This method is useful for debugging and monitoring
        purposes.

        Args:
            token: Authentication token to analyze

        Returns:
            Dictionary containing token information or None if token is invalid

        Example:
            >>> authenticator = ConnectionAuthenticator("shared-secret")
            >>> token = authenticator.generate_token()
            >>> info = authenticator.get_token_info(token)
            >>> print(f"Period: {info['period']}")
            >>> print(f"Hash: {info['hash'][:16]}...")
            Period: 5476800
            Hash: a1b2c3d4e5f6...
        """
        try:
            import base64
            import json

            # Decode token
            token_bytes = base64.b64decode(token.encode("utf-8"))
            token_data = json.loads(token_bytes.decode("utf-8"))

            return {
                "period": token_data.get("period"),
                "hash": token_data.get("hash"),
                "period_size": self.period_size,
                "num_sequential_hashes": self.num_sequential_hashes,
            }

        except (ValueError, json.JSONDecodeError, KeyError):
            return None
