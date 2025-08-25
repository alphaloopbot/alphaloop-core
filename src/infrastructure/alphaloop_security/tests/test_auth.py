"""Tests for authentication module."""

from alphaloop_security.auth import ConnectionAuthenticator
import pytest


class TestConnectionAuthenticator:
    """Test cases for ConnectionAuthenticator."""

    def test_initialization(self):
        """Test authenticator initialization."""
        auth = ConnectionAuthenticator(
            passphrase="test-passphrase", period_size=5, num_sequential_hashes=3
        )

        assert auth.passphrase == b"test-passphrase"
        assert auth.period_size == 5
        assert auth.num_sequential_hashes == 3

    def test_token_generation(self):
        """Test token generation."""
        auth = ConnectionAuthenticator(
            passphrase="test-passphrase", period_size=5, num_sequential_hashes=3
        )

        token = auth.generate_token()
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_validation(self):
        """Test token validation."""
        auth = ConnectionAuthenticator(
            passphrase="test-passphrase", period_size=5, num_sequential_hashes=3
        )

        # Generate a valid token
        token = auth.generate_token()

        # Validate the token
        is_valid = auth.validate_token(token)
        assert is_valid is True

    def test_invalid_token_validation(self):
        """Test invalid token validation."""
        auth = ConnectionAuthenticator(
            passphrase="test-passphrase", period_size=5, num_sequential_hashes=3
        )

        # Test with invalid token
        is_valid = auth.validate_token("invalid-token")
        assert is_valid is False

    def test_token_info(self):
        """Test token info extraction."""
        auth = ConnectionAuthenticator(
            passphrase="test-passphrase", period_size=5, num_sequential_hashes=3
        )

        # Generate a token
        token = auth.generate_token()

        # Get token info
        info = auth.get_token_info(token)
        assert info is not None
        assert "period" in info
        assert "hash" in info
        assert info["period_size"] == 5
        assert info["num_sequential_hashes"] == 3

    def test_invalid_token_info(self):
        """Test token info with invalid token."""
        auth = ConnectionAuthenticator(
            passphrase="test-passphrase", period_size=5, num_sequential_hashes=3
        )

        # Test with invalid token
        info = auth.get_token_info("invalid-token")
        assert info is None

    def test_custom_period_token(self):
        """Test token generation with custom period."""
        auth = ConnectionAuthenticator(
            passphrase="test-passphrase", period_size=5, num_sequential_hashes=3
        )

        # Generate token for specific period
        custom_period = 12345
        token = auth.generate_token(custom_period=custom_period)

        # Get token info to verify period
        info = auth.get_token_info(token)
        assert info is not None
        assert info["period"] == custom_period

    def test_tolerance_periods(self):
        """Test token validation with tolerance periods."""
        auth = ConnectionAuthenticator(
            passphrase="test-passphrase", period_size=5, num_sequential_hashes=3
        )

        # Generate a token
        token = auth.generate_token()

        # Validate with different tolerance levels
        assert auth.validate_token(token, tolerance_periods=0) is True
        assert auth.validate_token(token, tolerance_periods=1) is True
        assert auth.validate_token(token, tolerance_periods=2) is True

    def test_empty_passphrase_validation(self):
        """Test that empty passphrase raises ValueError."""
        with pytest.raises(ValueError, match="passphrase cannot be empty"):
            ConnectionAuthenticator(passphrase="", period_size=5)

        with pytest.raises(ValueError, match="passphrase cannot be empty"):
            ConnectionAuthenticator(passphrase="   ", period_size=5)

    def test_invalid_period_size(self):
        """Test that invalid period size raises ValueError."""
        with pytest.raises(ValueError, match="period_size must be positive"):
            ConnectionAuthenticator(passphrase="test", period_size=0)

        with pytest.raises(ValueError, match="period_size must be positive"):
            ConnectionAuthenticator(passphrase="test", period_size=-1)

    def test_invalid_sequential_hashes(self):
        """Test that invalid sequential hashes raises ValueError."""
        with pytest.raises(ValueError, match="num_sequential_hashes must be positive"):
            ConnectionAuthenticator(passphrase="test", num_sequential_hashes=0)

        with pytest.raises(ValueError, match="num_sequential_hashes must be positive"):
            ConnectionAuthenticator(passphrase="test", num_sequential_hashes=-1)
