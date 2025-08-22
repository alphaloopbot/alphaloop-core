#!/usr/bin/env python3
"""
Security Package Demo

This script demonstrates the usage of the AlphaLoop Security package
for authentication, encryption, and secure URL handling.
"""

import os
import sys

# Add the packages directory to the path
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "packages", "alphaloop-security", "src"),
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

    # Get current hash
    current_hash = auth.hash
    print(f"Current hash: {current_hash}")

    # Get sequential hashes
    sequential_hashes = auth.sequential_hashes
    print(f"Sequential hashes: {sequential_hashes}")

    # Validate hash
    try:
        auth.check(current_hash)
        print("✅ Hash validation successful")
    except UnauthorizedRequestError as e:
        print(f"❌ Hash validation failed: {e}")

    # Test invalid hash
    try:
        auth.check("invalid-hash")
        print("❌ Should have failed")
    except UnauthorizedRequestError:
        print("✅ Invalid hash correctly rejected")

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

    # Parse URL (simulate receiving the request)
    # In a real scenario, you'd extract h and d from the URL
    reader = SecureURLReader(
        passphrase="demo-secret-passphrase", period_size=5, num_sequential_hashes=3
    )

    # Extract hash and encrypted data from URL
    # This is a simplified example - in reality you'd parse the URL
    try:
        # For demo purposes, we'll encrypt again to get the values
        encrypted_data, hash_value = composer.encrypt_parameters(parameters)

        # Decrypt parameters
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
