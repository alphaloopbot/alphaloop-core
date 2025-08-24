"""Data integrity validation utilities."""

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .exceptions import IntegrityError


@dataclass
class DictionaryIntegrityValidator:
    """
    Validates the integrity of data using cryptographic hashes.

    This class provides methods to sign data with a hash and verify
    that the data hasn't been tampered with during transmission.
    """

    passphrase: str

    def get_hash(self, data_str: str) -> str:
        """
        Generate a hash for the given data string.

        Args:
            data_str: The data string to hash.

        Returns:
            A SHA-256 hash of the data with the passphrase.
        """
        data_to_hash = self.passphrase + data_str
        hash_value = hashlib.sha256(data_to_hash.encode("utf-8")).hexdigest()
        return hash_value

    def sign(self, data: dict[str, Any]) -> dict[str, str]:
        """
        Sign the data with a hash for integrity verification.

        Args:
            data: The data dictionary to sign.

        Returns:
            A dictionary containing the original data as JSON and its hash.
        """
        data_str_keys = json.dumps(data, sort_keys=True)
        return {"hash": self.get_hash(data_str_keys), "payload": data_str_keys}

    def check_hash(self, data: dict[str, str]) -> None:
        """
        Check if the hash in the data is correct.

        Args:
            data: The data dictionary containing 'hash' and 'payload' keys.

        Raises:
            IntegrityError: If the hash doesn't match the payload.
        """
        original_data = data.get("payload")
        hash_value = data.get("hash")

        if not original_data or not hash_value:
            raise IntegrityError("Missing required fields: 'hash' or 'payload'.")

        expected_hash = self.get_hash(original_data)
        if hash_value != expected_hash:
            raise IntegrityError("Data integrity compromised - hash mismatch.")

    def verify(self, data: dict[str, str]) -> dict[str, Any]:
        """
        Verify the data integrity and return the original data.

        Args:
            data: The data dictionary containing 'hash' and 'payload' keys.

        Returns:
            The original data as a dictionary.

        Raises:
            IntegrityError: If the data integrity check fails.
        """
        self.check_hash(data)
        try:
            return json.loads(data["payload"])
        except json.JSONDecodeError as e:
            raise IntegrityError(f"Failed to parse payload JSON: {str(e)}")

    def verify_and_validate(
        self, data: dict[str, str], required_keys: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Verify data integrity and validate required fields.

        Args:
            data: The data dictionary containing 'hash' and 'payload' keys.
            required_keys: List of keys that must be present in the payload.

        Returns:
            The original data as a dictionary.

        Raises:
            IntegrityError: If the data integrity check fails or required keys are missing.
        """
        verified_data = self.verify(data)

        if required_keys:
            missing_keys = [key for key in required_keys if key not in verified_data]
            if missing_keys:
                raise IntegrityError(f"Missing required keys: {missing_keys}")

        return verified_data
