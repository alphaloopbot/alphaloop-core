"""Tests for encryption module."""

import pytest
from alphaloop_security.encryption import DataEncryptor
from alphaloop_security.exceptions import EncryptionError


class TestDataEncryptor:
    """Test cases for DataEncryptor."""

    def test_initialization(self):
        """Test encryptor initialization."""
        encryptor = DataEncryptor(
            passphrase="test-passphrase", period_size=5, num_sequential_hashes=3
        )

        assert encryptor.passphrase == "test-passphrase"
        assert encryptor.period_size == 5
        assert encryptor.num_sequential_hashes == 3
        assert encryptor.connection_authenticator is not None

    def test_fernet_key_generation(self):
        """Test Fernet key generation."""
        encryptor = DataEncryptor(passphrase="test-passphrase", period_size=5)

        hash_value = "test-hash-value"
        key = encryptor.get_fernet_key(hash_value)

        assert isinstance(key, bytes)
        assert len(key) > 0

    def test_encryption_decryption(self):
        """Test basic encryption and decryption."""
        encryptor = DataEncryptor(passphrase="test-passphrase", period_size=5)

        original_data = "sensitive data to encrypt"
        encrypted_data, hash_value = encryptor.encrypt(original_data)

        assert isinstance(encrypted_data, str)
        assert isinstance(hash_value, str)
        assert len(encrypted_data) > 0
        assert len(hash_value) > 0

        # Decrypt the data
        decrypted_data = encryptor.decrypt(encrypted_data, hash_value)
        assert decrypted_data == original_data

    def test_encryption_with_special_characters(self):
        """Test encryption with special characters."""
        encryptor = DataEncryptor(passphrase="test-passphrase", period_size=5)

        original_data = (
            "sensitive data with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        )
        encrypted_data, hash_value = encryptor.encrypt(original_data)

        decrypted_data = encryptor.decrypt(encrypted_data, hash_value)
        assert decrypted_data == original_data

    def test_encryption_with_unicode(self):
        """Test encryption with unicode characters."""
        encryptor = DataEncryptor(passphrase="test-passphrase", period_size=5)

        original_data = "sensitive data with unicode: ñáéíóú 中文 русский"
        encrypted_data, hash_value = encryptor.encrypt(original_data)

        decrypted_data = encryptor.decrypt(encrypted_data, hash_value)
        assert decrypted_data == original_data

    def test_invalid_decryption(self):
        """Test decryption with wrong hash."""
        encryptor = DataEncryptor(passphrase="test-passphrase", period_size=5)

        original_data = "sensitive data"
        encrypted_data, _ = encryptor.encrypt(original_data)

        with pytest.raises(EncryptionError):
            encryptor.decrypt(encrypted_data, "wrong-hash")

    def test_invalid_encrypted_data(self):
        """Test decryption with invalid encrypted data."""
        encryptor = DataEncryptor(passphrase="test-passphrase", period_size=5)

        with pytest.raises(EncryptionError):
            encryptor.decrypt("invalid-encrypted-data", "some-hash")

    def test_base64_validation(self):
        """Test Base64 validation."""
        encryptor = DataEncryptor(passphrase="test-passphrase", period_size=5)

        # Valid Base64
        assert encryptor.is_valid_base64("dGVzdA==") is True

        # Invalid Base64
        assert encryptor.is_valid_base64("invalid-base64!@#") is False
        assert encryptor.is_valid_base64("") is False

    def test_padding_operations(self):
        """Test padding addition and removal."""
        encryptor = DataEncryptor(passphrase="test-passphrase", period_size=5)

        # Test padding removal
        data_with_padding = "dGVzdA=="
        data_without_padding = encryptor._remove_padding(data_with_padding)
        assert data_without_padding == "dGVzdA"

        # Test padding addition
        data_without_padding = "dGVzdA"
        data_with_padding = encryptor._add_padding(data_without_padding)
        assert data_with_padding == "dGVzdA=="

    def test_empty_string_encryption(self):
        """Test encryption of empty string."""
        encryptor = DataEncryptor(passphrase="test-passphrase", period_size=5)

        original_data = ""
        encrypted_data, hash_value = encryptor.encrypt(original_data)

        decrypted_data = encryptor.decrypt(encrypted_data, hash_value)
        assert decrypted_data == original_data

    def test_large_data_encryption(self):
        """Test encryption of large data."""
        encryptor = DataEncryptor(passphrase="test-passphrase", period_size=5)

        original_data = "x" * 10000  # 10KB of data
        encrypted_data, hash_value = encryptor.encrypt(original_data)

        decrypted_data = encryptor.decrypt(encrypted_data, hash_value)
        assert decrypted_data == original_data
