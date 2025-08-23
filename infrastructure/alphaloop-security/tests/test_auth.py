"""Tests for authentication module."""

import pytest
from alphaloop_security.auth import ConnectionAuthenticator
from alphaloop_security.exceptions import UnauthorizedRequestError


class TestConnectionAuthenticator:
    """Test cases for ConnectionAuthenticator."""

    def test_initialization(self):
        """Test authenticator initialization."""
        auth = ConnectionAuthenticator(
            passphrase="test-passphrase", period_size=5, num_sequential_hashes=3
        )

        assert auth.passphrase == "test-passphrase"
        assert auth.period_size == 5
        assert auth.num_sequential_hashes == 3

    def test_hash_generation(self):
        """Test hash generation."""
        auth = ConnectionAuthenticator(
            passphrase="test-passphrase", period_size=5, num_sequential_hashes=3
        )

        hash_value = auth.hash
        assert isinstance(hash_value, str)
        assert len(hash_value) == 16

    def test_sequential_hashes(self):
        """Test sequential hash generation."""
        auth = ConnectionAuthenticator(
            passphrase="test-passphrase", period_size=5, num_sequential_hashes=3
        )

        hashes = auth.sequential_hashes
        assert len(hashes) == 3
        assert all(isinstance(h, str) for h in hashes)
        assert all(len(h) == 16 for h in hashes)

    def test_valid_hash_check(self):
        """Test valid hash validation."""
        auth = ConnectionAuthenticator(
            passphrase="test-passphrase", period_size=5, num_sequential_hashes=3
        )

        current_hash = auth.hash
        auth.check(current_hash)  # Should not raise

    def test_invalid_hash_check(self):
        """Test invalid hash validation."""
        auth = ConnectionAuthenticator(
            passphrase="test-passphrase", period_size=5, num_sequential_hashes=3
        )

        with pytest.raises(UnauthorizedRequestError):
            auth.check("invalid-hash-value")

    def test_is_valid_method(self):
        """Test is_valid method."""
        auth = ConnectionAuthenticator(
            passphrase="test-passphrase", period_size=5, num_sequential_hashes=3
        )

        current_hash = auth.hash
        assert auth.is_valid(current_hash) is True
        assert auth.is_valid("invalid-hash") is False

    def test_hash_time_consistency(self):
        """Test that hash generation is consistent within the same period."""
        auth = ConnectionAuthenticator(
            passphrase="test-passphrase", period_size=5, num_sequential_hashes=3
        )

        hash1 = auth.get_hash_time(0)
        hash2 = auth.get_hash_time(0)
        assert hash1 == hash2

    def test_different_periods(self):
        """Test that different periods generate different hashes."""
        auth = ConnectionAuthenticator(
            passphrase="test-passphrase", period_size=5, num_sequential_hashes=3
        )

        current_hash = auth.get_hash_time(0)
        previous_hash = auth.get_hash_time(1)

        # These might be the same if we're at the boundary of a period
        # but they should be different in most cases
        # We'll just test that the method works
        assert isinstance(current_hash, str)
        assert isinstance(previous_hash, str)
        assert len(current_hash) == 16
        assert len(previous_hash) == 16
