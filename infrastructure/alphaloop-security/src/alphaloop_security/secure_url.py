"""Secure URL composition and parsing utilities."""

import json
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from .auth import ConnectionAuthenticator
from .encryption import DataEncryptor
from .exceptions import EncryptionError, UnauthorizedRequestError


@dataclass
class SecureURLComposer:
    """
    Builds secure URLs with encrypted parameters and time-based authentication.

    This class creates URLs that include encrypted parameters and a time-based
    hash for authentication, ensuring secure communication between services.
    """

    target_ip: str
    target_port: int
    endpoint: str
    passphrase: str
    https: bool = False
    period_size: int = 5  # The period size in seconds

    def __post_init__(self) -> None:
        """Initialize the data encryptor."""
        self.data_encryptor = DataEncryptor(
            passphrase=self.passphrase, period_size=self.period_size
        )

    def is_valid_base64(self, data: str) -> bool:
        """
        Check if the given data is valid Base64.

        Args:
            data: The data to validate.

        Returns:
            True if the data is valid Base64, False otherwise.
        """
        return self.data_encryptor.is_valid_base64(data)

    def create_unicode(self) -> str:
        """
        Create a unique identifier for request tracking.

        Returns:
            A unique string combining timestamp and UUID.
        """
        timestamp = int(time.time() * 1000)
        t_code = str(timestamp)[-6:]
        uuid_code = str(uuid.uuid4()).split("-")[-1]
        unicode_value = f"{t_code}-{uuid_code}"
        return unicode_value

    def insert_unicode(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Insert a unicode identifier into the data dictionary.

        Args:
            data: The data dictionary to modify.

        Returns:
            The data dictionary with the unicode field added.
        """
        data_copy = data.copy()
        data_copy["unicode"] = self.create_unicode()
        return data_copy

    def encrypt_parameters(self, data: dict[str, Any]) -> tuple[str, str]:
        """
        Encrypt the given parameters.

        Args:
            data: The parameters to encrypt.

        Returns:
            A tuple of (encrypted_data, hash_value).

        Raises:
            EncryptionError: If encryption fails.
        """
        try:
            encrypted_data, hash_value = self.data_encryptor.encrypt(json.dumps(data))
            return encrypted_data, hash_value
        except Exception as e:
            raise EncryptionError(f"Parameter encryption failed: {str(e)}")

    def build_url(self, parameters: dict[str, Any]) -> str:
        """
        Build a secure URL with encrypted parameters.

        Args:
            parameters: The parameters to include in the URL.

        Returns:
            A secure URL with encrypted parameters and authentication hash.
        """
        parameters_with_unicode = self.insert_unicode(parameters)
        encrypted_data, hash_value = self.encrypt_parameters(parameters_with_unicode)

        protocol = "https" if self.https else "http"
        return f"{protocol}://{self.target_ip}:{self.target_port}{self.endpoint}?h={hash_value}&d={encrypted_data}"


@dataclass
class SecureURLReader:
    """
    Reads and validates secure URLs with encrypted parameters.

    This class decrypts URL parameters and validates the time-based
    authentication hash, preventing replay attacks.
    """

    passphrase: str
    period_size: int = 5  # The period size in seconds
    num_sequential_hashes: int = 3  # The number of sequential hashes to store
    nonvalid_unicodes: deque = field(
        default_factory=lambda: deque()
    )  # Store codes for the last 60 seconds

    def __post_init__(self) -> None:
        """Initialize the data encryptor and connection authenticator."""
        self.data_encryptor = DataEncryptor(
            passphrase=self.passphrase,
            period_size=self.period_size,
            num_sequential_hashes=self.num_sequential_hashes,
        )
        self.connection_authenticator = ConnectionAuthenticator(
            passphrase=self.passphrase,
            period_size=self.period_size,
            num_sequential_hashes=self.num_sequential_hashes,
        )

    def check_hash(self, hash_value: str) -> None:
        """
        Check if the given hash is valid.

        Args:
            hash_value: The hash to validate.

        Raises:
            UnauthorizedRequestError: If the hash is not valid.
        """
        self.connection_authenticator.check(hash_value)

    def decrypt_parameters(
        self, encrypted_data: str, hash_value: str
    ) -> dict[str, Any]:
        """
        Decrypt the given URL parameters.

        Args:
            encrypted_data: The encrypted parameters.
            hash_value: The hash used for encryption.

        Returns:
            The decrypted parameters as a dictionary.

        Raises:
            EncryptionError: If decryption fails.
        """
        try:
            json_data = self.data_encryptor.decrypt(encrypted_data, hash_value)
            return json.loads(json_data)
        except json.JSONDecodeError as e:
            raise EncryptionError(f"Failed to parse decrypted JSON: {str(e)}")
        except Exception as e:
            raise EncryptionError(f"Parameter decryption failed: {str(e)}")

    def check_valid_unicode(self, unicode_value: str) -> None:
        """
        Check if the given unicode is valid (not previously used).

        Args:
            unicode_value: The unicode to validate.

        Raises:
            UnauthorizedRequestError: If the unicode has been used before.
        """
        for _, stored_unicode in self.nonvalid_unicodes:
            if unicode_value == stored_unicode:
                raise UnauthorizedRequestError(
                    "Token error - duplicate request detected."
                )

    def register_unicode(self, unicode_value: str) -> None:
        """
        Register the given unicode to prevent replay attacks.

        Args:
            unicode_value: The unicode to register.
        """
        current_time = datetime.now()
        # Append the new code with its timestamp
        self.nonvalid_unicodes.append((current_time, unicode_value))
        # Remove codes older than one minute
        one_minute_ago = current_time - timedelta(seconds=60)
        while self.nonvalid_unicodes and self.nonvalid_unicodes[0][0] < one_minute_ago:
            self.nonvalid_unicodes.popleft()

    def __call__(self, encrypted_data: str, hash_value: str) -> dict[str, Any]:
        """
        Process a secure URL request.

        This method validates the hash, decrypts the parameters, and
        checks for replay attacks using the unicode identifier.

        Args:
            encrypted_data: The encrypted parameters.
            hash_value: The authentication hash.

        Returns:
            The decrypted parameters.

        Raises:
            UnauthorizedRequestError: If authentication or validation fails.
            EncryptionError: If decryption fails.
        """
        # Check hash validity
        self.check_hash(hash_value)

        # Decrypt the parameters
        parameters = self.decrypt_parameters(encrypted_data, hash_value)

        # Check if the unicode is valid
        unicode_value = parameters.get("unicode")
        if not unicode_value:
            raise UnauthorizedRequestError("Missing unicode identifier.")

        self.check_valid_unicode(unicode_value)

        # Register the unicode to prevent duplicate requests
        self.register_unicode(unicode_value)

        return parameters
