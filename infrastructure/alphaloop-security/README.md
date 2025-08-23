# AlphaLoop Security Package

A comprehensive security package for AlphaLoop Core providing encryption, authentication, and secure URL handling utilities.

## Features

- **Time-based Authentication**: Secure connection authentication using time-based hashing
- **Data Encryption**: AES encryption with time-based keys using Fernet
- **Secure URLs**: Build and parse secure URLs with encrypted parameters
- **Data Integrity**: Cryptographic hash-based data integrity validation
- **Replay Attack Prevention**: Unique request identifiers to prevent replay attacks

## Installation

```bash
# From the infrastructure directory
cd infrastructure/alphaloop-security
poetry install
```

## Quick Start

### Authentication

```python
from alphaloop_security import ConnectionAuthenticator

# Create an authenticator with 5-second periods
auth = ConnectionAuthenticator(
    passphrase="your-secret-passphrase",
    period_size=5,
    num_sequential_hashes=3
)

# Get current hash
current_hash = auth.hash

# Validate a hash
try:
    auth.check("some-hash-value")
    print("Hash is valid!")
except UnauthorizedRequestError:
    print("Hash is invalid or expired")
```

### Encryption

```python
from alphaloop_security import DataEncryptor

# Create an encryptor
encryptor = DataEncryptor(
    passphrase="your-secret-passphrase",
    period_size=5
)

# Encrypt data
encrypted_data, hash_value = encryptor.encrypt("sensitive data")

# Decrypt data
decrypted_data = encryptor.decrypt(encrypted_data, hash_value)
```

### Secure URLs

```python
from alphaloop_security import SecureURLComposer, SecureURLReader

# Create a URL composer
composer = SecureURLComposer(
    target_ip="192.168.1.100",
    target_port=8080,
    endpoint="/api/data",
    passphrase="your-secret-passphrase"
)

# Build a secure URL
parameters = {"user_id": 123, "action": "get_data"}
secure_url = composer.build_url(parameters)

# Parse and validate the URL
reader = SecureURLReader(
    passphrase="your-secret-passphrase",
    period_size=5,
    num_sequential_hashes=3
)

# Extract parameters from URL (you'd get these from the request)
decrypted_params = reader(encrypted_data, hash_value)
```

### Data Integrity

```python
from alphaloop_security import DictionaryIntegrityValidator

# Create a validator
validator = DictionaryIntegrityValidator(passphrase="your-secret-passphrase")

# Sign data
data = {"user_id": 123, "timestamp": "2024-01-01T00:00:00Z"}
signed_data = validator.sign(data)

# Verify data integrity
verified_data = validator.verify(signed_data)
```

## Security Features

### Time-based Authentication
- Uses time periods to generate authentication hashes
- Supports multiple sequential hashes for tolerance
- Automatically expires after the configured period

### Encryption
- Uses AES-256 encryption via Fernet
- Time-based key derivation with PBKDF2
- Increased iterations (100,000) for better security
- URL-safe Base64 encoding

### Replay Attack Prevention
- Unique request identifiers (unicode)
- Automatic cleanup of old identifiers
- 60-second window for duplicate detection

### Data Integrity
- SHA-256 hashing with passphrase
- Deterministic JSON serialization
- Comprehensive error handling

## API Reference

### ConnectionAuthenticator

Authenticates connections using time-based hashing.

**Parameters:**
- `passphrase`: Secret passphrase for hash generation
- `period_size`: Time period in seconds
- `num_sequential_hashes`: Number of sequential hashes to store

**Methods:**
- `get_hash_time(previous_period_seq=0)`: Get hash for specific time period
- `hash`: Property to get current period's hash
- `sequential_hashes`: Property to get list of valid hashes
- `check(hash_value)`: Validate a hash (raises exception if invalid)
- `is_valid(hash_value)`: Check if hash is valid (returns boolean)

### DataEncryptor

Encrypts and decrypts data using time-based keys.

**Parameters:**
- `passphrase`: Secret passphrase for key derivation
- `period_size`: Time period in seconds
- `num_sequential_hashes`: Number of sequential hashes to store

**Methods:**
- `encrypt(data)`: Encrypt data and return (encrypted_data, hash)
- `decrypt(encrypted_data, hash_value)`: Decrypt data
- `is_valid_base64(data)`: Check if data is valid Base64

### SecureURLComposer

Builds secure URLs with encrypted parameters.

**Parameters:**
- `target_ip`: Target server IP address
- `target_port`: Target server port
- `endpoint`: API endpoint path
- `passphrase`: Secret passphrase
- `https`: Use HTTPS (default: False)
- `period_size`: Time period in seconds

**Methods:**
- `build_url(parameters)`: Build secure URL with encrypted parameters

### SecureURLReader

Reads and validates secure URLs.

**Parameters:**
- `passphrase`: Secret passphrase
- `period_size`: Time period in seconds
- `num_sequential_hashes`: Number of sequential hashes to store
- `nonvalid_unicodes`: Queue for tracking used identifiers

**Methods:**
- `__call__(encrypted_data, hash_value)`: Process secure URL request

### DictionaryIntegrityValidator

Validates data integrity using cryptographic hashes.

**Parameters:**
- `passphrase`: Secret passphrase for hash generation

**Methods:**
- `sign(data)`: Sign data with hash
- `verify(data)`: Verify data integrity
- `verify_and_validate(data, required_keys)`: Verify and validate required fields

## Error Handling

The package provides specific exception types:

- `SecurityError`: Base exception for all security errors
- `UnauthorizedRequestError`: Authentication or authorization failures
- `EncryptionError`: Encryption/decryption failures
- `IntegrityError`: Data integrity violations

## Best Practices

1. **Use Strong Passphrases**: Choose long, random passphrases
2. **Configure Appropriate Periods**: Balance security with usability
3. **Handle Exceptions**: Always catch and handle security exceptions
4. **Validate Input**: Validate all input data before processing
5. **Secure Storage**: Store passphrases securely (environment variables, etc.)
6. **Regular Updates**: Keep dependencies updated for security patches

## Development

```bash
# Install development dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Run linting
poetry run ruff check .

# Run type checking
poetry run mypy src/
```

## License

This package is part of the AlphaLoop Core project.
