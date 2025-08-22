"""Data encryption and decryption utilities."""

import base64
import binascii
from dataclasses import dataclass

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .auth import ConnectionAuthenticator
from .exceptions import EncryptionError


@dataclass
class DataEncryptor:
    """
    Encrypts and decrypts data using time-based keys.

    This class uses the ConnectionAuthenticator to generate time-based keys
    for encryption, ensuring that encrypted data has a limited lifespan.
    """

    passphrase: str
    period_size: int  # The period size in seconds
    num_sequential_hashes: int = 1  # The number of sequential hashes to store

    def __post_init__(self) -> None:
        """Initialize the connection authenticator."""
        self.connection_authenticator = ConnectionAuthenticator(
            passphrase=self.passphrase,
            period_size=self.period_size,
            num_sequential_hashes=self.num_sequential_hashes,
        )
        self._encryption_fernet: Fernet | None = None
        self._encryption_hash: str | None = None

    def get_fernet_key(self, hash_value: str) -> bytes:
        """
        Generate a Fernet key from the hash value.

        Args:
            hash_value: The hash value to use as salt.

        Returns:
            A Fernet-compatible key.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # Fernet keys are 32 bytes
            salt=hash_value.encode(),
            iterations=100000,  # Increased from 10 for better security
            backend=default_backend(),
        )
        return base64.urlsafe_b64encode(kdf.derive(self.passphrase.encode()))

    def update_fernet_key(self) -> None:
        """
        Update the Fernet key for encryption.

        This method generates a new key based on the current time period.
        """
        hash_value = self.connection_authenticator.hash
        key = self.get_fernet_key(hash_value)
        self._encryption_fernet = Fernet(key)
        self._encryption_hash = hash_value

    def _remove_padding(self, encrypted_data: str) -> str:
        """
        Remove padding from encrypted data.

        Args:
            encrypted_data: The encrypted data with padding.

        Returns:
            The encrypted data without padding.
        """
        return encrypted_data.rstrip("=")

    def encrypt(self, data: str) -> tuple[str, str]:
        """
        Encrypt the given data.

        Args:
            data: The data to encrypt.

        Returns:
            A tuple of (encrypted_data, hash_value).

        Raises:
            EncryptionError: If encryption fails.
        """
        try:
            self.update_fernet_key()
            if self._encryption_fernet is None or self._encryption_hash is None:
                raise EncryptionError("Failed to initialize encryption key.")

            # Encrypt the data
            encrypted_data = self._encryption_fernet.encrypt(data.encode())
            # Encode to Base64
            url_safe_encrypted_data = base64.urlsafe_b64encode(encrypted_data).decode()
            # Remove padding
            no_pad_url_safe_encrypted_data = self._remove_padding(
                url_safe_encrypted_data
            )

            return no_pad_url_safe_encrypted_data, self._encryption_hash
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {str(e)}")

    def _add_padding(self, encrypted_data: str) -> str:
        """
        Add padding to encrypted data.

        Args:
            encrypted_data: The encrypted data without padding.

        Returns:
            The encrypted data with proper padding.
        """
        return encrypted_data + "=" * (4 - len(encrypted_data) % 4)

    def decrypt(self, encrypted_data: str, hash_value: str) -> str:
        """
        Decrypt the given data.

        Args:
            encrypted_data: The encrypted data.
            hash_value: The hash value used for encryption.

        Returns:
            The decrypted data.

        Raises:
            EncryptionError: If decryption fails.
        """
        try:
            fernet_key = self.get_fernet_key(hash_value)
            # Add padding
            padded_encrypted_data = self._add_padding(encrypted_data)
            # Decode from Base64
            base64_encrypted_data = base64.urlsafe_b64decode(
                padded_encrypted_data.encode()
            )
            # Decrypt
            decrypted_data = Fernet(fernet_key).decrypt(base64_encrypted_data)
            return decrypted_data.decode()
        except (binascii.Error, UnicodeDecodeError) as e:
            raise EncryptionError(f"Decryption failed: {str(e)}")
        except Exception as e:
            raise EncryptionError(f"Decryption failed: {str(e)}")

    def is_valid_base64(self, data: str) -> bool:
        """
        Check if the given data is valid Base64.

        Args:
            data: The data to validate.

        Returns:
            True if the data is valid Base64, False otherwise.
        """
        try:
            base64.urlsafe_b64decode(data)
            return True
        except (TypeError, binascii.Error):
            return False
