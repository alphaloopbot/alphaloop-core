"""AlphaLoop Security Package

Provides encryption, authentication, and secure URL handling utilities.
"""

__version__ = "0.1.0"
__author__ = "Didac Cristobal-Canals"
__email__ = "didac.crst@gmail.com"

from .auth import ConnectionAuthenticator
from .encryption import DataEncryptor
from .exceptions import (
    EncryptionError,
    IntegrityError,
    SecurityError,
    UnauthorizedRequestError,
)
from .integrity import DictionaryIntegrityValidator
from .secure_url import SecureURLComposer, SecureURLReader

__all__ = [
    "ConnectionAuthenticator",
    "DataEncryptor",
    "SecureURLComposer",
    "SecureURLReader",
    "DictionaryIntegrityValidator",
    "SecurityError",
    "UnauthorizedRequestError",
    "EncryptionError",
    "IntegrityError",
]
