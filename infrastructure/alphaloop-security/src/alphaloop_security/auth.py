"""Authentication utilities for secure connections."""

import hashlib
import time
from dataclasses import dataclass

from .exceptions import UnauthorizedRequestError


@dataclass
class ConnectionAuthenticator:
    """
    Authenticates connections using time-based hashing.

    This class generates time-based hashes that expire after a specified period,
    allowing for secure authentication without storing long-lived tokens.
    """

    passphrase: str
    period_size: int  # The period size in seconds
    num_sequential_hashes: int  # The number of sequential hashes to store

    def get_hash_time(self, previous_period_seq: int = 0) -> str:
        """
        Generate a hash based on the passphrase and time period.

        Args:
            previous_period_seq: The period sequence to hash the passphrase with.
                0 is the current period, 1 is the previous period, etc.

        Returns:
            A 16-character hash string.
        """
        current_period_time = int(time.time()) // self.period_size
        period_time = current_period_time - previous_period_seq
        phrase = f"{self.passphrase}{period_time}"
        hash_value = hashlib.md5(phrase.encode()).hexdigest()
        return hash_value[10:26]

    @property
    def hash(self) -> str:
        """Get the current period's hash."""
        return self.get_hash_time()

    @property
    def sequential_hashes(self) -> list[str]:
        """
        Get a list of sequential hashes for the current and previous periods.

        This is useful to ensure that the user can still authenticate even if
        the previous hash just expired.

        Returns:
            List of hash strings for the current and previous periods.
        """
        return [self.get_hash_time(i) for i in range(self.num_sequential_hashes)]

    def check(self, hash_value: str) -> None:
        """
        Check if the given hash is valid (in the list of sequential hashes).

        Args:
            hash_value: The hash to validate.

        Raises:
            UnauthorizedRequestError: If the hash is not valid.
        """
        sequential_hashes = self.sequential_hashes
        if hash_value not in sequential_hashes:
            raise UnauthorizedRequestError("Authentication error.")

    def is_valid(self, hash_value: str) -> bool:
        """
        Check if the given hash is valid without raising an exception.

        Args:
            hash_value: The hash to validate.

        Returns:
            True if the hash is valid, False otherwise.
        """
        try:
            self.check(hash_value)
            return True
        except UnauthorizedRequestError:
            return False
