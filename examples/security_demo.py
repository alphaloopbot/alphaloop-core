#!/usr/bin/env python3
"""
Security Package Demo

This script demonstrates the usage of the AlphaLoop Security package
for authentication, encryption, and secure URL handling.
"""

import os
import sys

# Add the infrastructure directory to the path
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "infrastructure", "alphaloop-security", "src"),
)

from alphaloop_security import (
    ConnectionAuthenticator,
    DataEncryptor,
    DictionaryIntegrityValidator,
    EncryptionError,
    IntegrityError,
    SecureURLComposer,
    SecureURLReader,
    UnauthorizedRequestError,
)


def demo_authentication():
    """Demonstrate authentication functionality."""
    print("🔐 Authentication Demo")
    print("=" * 50)

    # Create an authenticator
    auth = ConnectionAuthenticator(
        passphrase="demo-secret-passphrase", period_size=5, num_sequential_hashes=3
    )

    # Generate current token
    current_token = auth.generate_token()
    print(f"Current token: {current_token}")

    # Derive tokens for adjacent periods (handles clock drift)
    info = auth.get_token_info(current_token) or {}
    period = info.get("period")
    sequential_tokens = (
        [auth.generate_token(custom_period=p) for p in (period - 1, period, period + 1)]
        if period is not None
        else []
    )
    print(f"Sequential tokens: {sequential_tokens}")

    # Validate token (supports both exception- and bool-based APIs)
    check_fn = getattr(auth, "check", None)
    if callable(check_fn):
        try:
            check_fn(current_token)
            print("✅ Token validation successful")
        except UnauthorizedRequestError as e:
            print(f"❌ Token validation failed: {e}")
    else:
        if auth.validate_token(current_token):
            print("✅ Token validation successful")
        else:
            print("❌ Token validation failed")

    # Test invalid token
    invalid_token = "invalid-token"
    if callable(check_fn):
        try:
            check_fn(invalid_token)
            print("❌ Should have failed")
        except UnauthorizedRequestError:
            print("✅ Invalid token correctly rejected")
    else:
        if not auth.validate_token(invalid_token):
            print("✅ Invalid token correctly rejected")
        else:
            print("❌ Should have failed")

    print()


def demo_encryption():
    """Demonstrate encryption functionality."""
    print("🔒 Encryption Demo")
    print("=" * 50)

    # Create an encryptor
    encryptor = DataEncryptor(passphrase="demo-secret-passphrase", period_size=5)

    # Test data
    original_data = "This is sensitive data that needs to be encrypted!"
    print(f"Original data: {original_data}")

    # Encrypt data
    encrypted_data, hash_value = encryptor.encrypt(original_data)
    print(f"Encrypted data: {encrypted_data}")
    print(f"Hash: {hash_value}")

    # Decrypt data
    decrypted_data = encryptor.decrypt(encrypted_data, hash_value)
    print(f"Decrypted data: {decrypted_data}")

    # Verify
    if original_data == decrypted_data:
        print("✅ Encryption/decryption successful")
    else:
        print("❌ Encryption/decryption failed")

    # Test with wrong hash
    try:
        encryptor.decrypt(encrypted_data, "wrong-hash")
        print("❌ Should have failed")
    except EncryptionError:
        print("✅ Wrong hash correctly rejected")

    print()


def demo_secure_urls():
    """Demonstrate secure URL functionality."""
    print("🔗 Secure URL Demo")
    print("=" * 50)

    # Create URL composer
    composer = SecureURLComposer(
        target_ip="192.168.1.100",
        target_port=8080,
        endpoint="/api/data",
        passphrase="demo-secret-passphrase",
    )

    # Parameters to encrypt
    parameters = {
        "user_id": 123,
        "action": "get_data",
        "timestamp": "2024-01-01T00:00:00Z",
    }
    print(f"Original parameters: {parameters}")

    # Build secure URL
    secure_url = composer.build_url(parameters)
    print(f"Secure URL: {secure_url}")

    # Parse URL (simulate receiving the request) and extract h and d
    reader = SecureURLReader(
        passphrase="demo-secret-passphrase", period_size=5, num_sequential_hashes=3
    )

    # Extract token (h) and encrypted payload (d) from the URL
    try:
        from urllib.parse import parse_qs, urlparse

        parsed = urlparse(secure_url)
        qs = parse_qs(parsed.query)
        hash_value = qs.get("h", [None])[0]
        encrypted_data = qs.get("d", [None])[0]
        if not hash_value or not encrypted_data:
            raise ValueError("Missing 'h' (token) or 'd' (encrypted data) in URL.")

        # Decrypt parameters (will include 'unicode'; replay protection applies)
        decrypted_params = reader(encrypted_data, hash_value)
        print(f"Decrypted parameters: {decrypted_params}")

        # Verify (note: decrypted_params will have an extra 'unicode' field)
        if parameters["user_id"] == decrypted_params["user_id"]:
            print("✅ Secure URL processing successful")
        else:
            print("❌ Secure URL processing failed")

    except (UnauthorizedRequestError, EncryptionError) as e:
        print(f"❌ Secure URL processing failed: {e}")

    print()


def demo_data_integrity():
    """Demonstrate data integrity functionality."""
    print("🛡️ Data Integrity Demo")
    print("=" * 50)

    # Create validator
    validator = DictionaryIntegrityValidator(passphrase="demo-secret-passphrase")

    # Test data
    data = {
        "user_id": 123,
        "action": "update_profile",
        "timestamp": "2024-01-01T00:00:00Z",
        "data": {"name": "John Doe", "email": "john@example.com"},
    }
    print(f"Original data: {data}")

    # Sign data
    signed_data = validator.sign(data)
    print(f"Signed data: {signed_data}")

    # Verify data
    verified_data = validator.verify(signed_data)
    print(f"Verified data: {verified_data}")

    # Verify
    if data == verified_data:
        print("✅ Data integrity verification successful")
    else:
        print("❌ Data integrity verification failed")

    # Test tampered data
    tampered_data = signed_data.copy()
    tampered_data["payload"] = '{"user_id": 999, "action": "malicious_action"}'

    try:
        validator.verify(tampered_data)
        print("❌ Should have failed")
    except IntegrityError:
        print("✅ Tampered data correctly rejected")

    print()


def main():
    """Run all security demos."""
    print("🚀 AlphaLoop Security Package Demo")
    print("=" * 60)
    print()

    try:
        demo_authentication()
        demo_encryption()
        demo_secure_urls()
        demo_data_integrity()

        print("🎉 All demos completed successfully!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
