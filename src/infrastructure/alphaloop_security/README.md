# AlphaLoop Security Module

A comprehensive security system for AlphaLoop services, providing authentication, encryption, secure URLs, and data integrity validation.

## 🔒 Overview

The AlphaLoop Security module provides a comprehensive security solution for all AlphaLoop services. It modernizes security with:

- **Time-based Authentication** - Secure token-based authentication
- **Data Encryption** - AES-256 encryption with Fernet
- **Secure URLs** - Encrypted URL parameters and validation
- **Data Integrity** - Cryptographic hash-based validation
- **Integration Ready** - Works with all alphaloop-core services

## 🚀 Features

- ✅ **Authentication** - Time-based token authentication
- ✅ **Encryption** - AES-256 encryption with Fernet
- ✅ **Secure URLs** - Encrypted URL parameters
- ✅ **Data Integrity** - Hash-based validation
- ✅ **Async Support** - Non-blocking operations
- ✅ **Type Safety** - Full type hints

## 🔧 Usage

### **Importing the Module**

```python
# This is an internal module - no installation needed
from alphaloop_security import ConnectionAuthenticator, DataEncryptor, SecureURL
```

### **Basic Authentication**

```python
from alphaloop_security import ConnectionAuthenticator

# Create authenticator
authenticator = ConnectionAuthenticator("your-secret-key")

# Generate authentication token
token = authenticator.generate_token("user123", window_minutes=5)

# Verify token
is_valid = authenticator.verify_token(token, "user123")
print(f"Token valid: {is_valid}")
```

### **Data Encryption**

```python
from alphaloop_security import DataEncryptor

# Create encryptor
encryptor = DataEncryptor("your-encryption-key")

# Encrypt data
encrypted_data = encryptor.encrypt("sensitive data")
print(f"Encrypted: {encrypted_data}")

# Decrypt data
decrypted_data = encryptor.decrypt(encrypted_data)
print(f"Decrypted: {decrypted_data}")
```

### **Secure URLs**

```python
from alphaloop_security import SecureURL

# Create secure URL handler
secure_url = SecureURL("your-secret-key")

# Create secure URL
params = {"user_id": "123", "action": "view"}
secure_url_string = secure_url.create_secure_url("/api/data", params)
print(f"Secure URL: {secure_url_string}")

# Validate secure URL
is_valid = secure_url.validate_secure_url(secure_url_string)
print(f"URL valid: {is_valid}")
```

### **Using in Services**

```python
# Example: API Service with Authentication
from alphaloop_security import ConnectionAuthenticator

class APIService:
    def __init__(self):
        # Initialize authentication
        self.authenticator = ConnectionAuthenticator("api-secret-key")

    def handle_request(self, token, user_id):
        # Verify authentication
        if self.authenticator.verify_token(token, user_id):
            return "Access granted"
        else:
            return "Access denied"
```

## ⚙️ Configuration

### **Environment Variables**

```bash
# Security Configuration
SECURITY_SECRET_KEY=your-secret-key
SECURITY_TIME_WINDOW=300
SECURITY_ENCRYPTION_KEY=your-encryption-key
SECURITY_HASH_ALGORITHM=SHA256
```

### **Configuration from Environment**

```python
from alphaloop_security import SecurityConfig

# Load from environment
config = SecurityConfig.from_env()
print(f"Time window: {config.time_window}s")
```

## 🧪 Testing

```bash
# Test this module
cd src/infrastructure/alphaloop-security
python -m pytest tests/

# Test integration with alphaloop-core
make test-core
```

## 📚 API Reference

### **ConnectionAuthenticator**

**Methods:**
- `generate_token(user_id, window_minutes)`: Generate authentication token
- `verify_token(token, user_id)`: Verify token validity
- `get_token_info(token)`: Get token information

### **DataEncryptor**

**Methods:**
- `encrypt(data)`: Encrypt data
- `decrypt(encrypted_data)`: Decrypt data
- `is_encrypted(data)`: Check if data is encrypted

### **SecureURL**

**Methods:**
- `create_secure_url(path, params)`: Create secure URL
- `validate_secure_url(url)`: Validate secure URL
- `extract_params(url)`: Extract parameters from URL

### **SecurityConfig**

**Methods:**
- `from_env()`: Create config from environment variables
- `validate()`: Validate configuration settings

## 🎯 Key Points

- **Internal module** - part of alphaloop-core
- **No installation needed** - direct import
- **No versioning** - evolves with alphaloop-core
- **Used by all services** - system-metrics, market-data, etc.

---

**🎯 Goal**: This security module provides a solid foundation for authentication and encryption across all alphaloop-core services.
