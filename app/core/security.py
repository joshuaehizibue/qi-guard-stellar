"""
Cryptographic utilities for API key generation, prefix parsing, and SHA-256 hashing.
"""

import hashlib
import secrets
from typing import Tuple


def generate_api_key(key_type: str = "live") -> Tuple[str, str, str]:
    """
    Generates a new API key.
    
    Returns:
        Tuple[raw_key, prefix, hashed_key]
        e.g., ("qig_live_1234567890abcdef...", "qig_live_1234", "sha256_hash...")
    """
    random_bytes = secrets.token_hex(24)
    raw_key = f"qig_{key_type}_{random_bytes}"
    prefix = raw_key[:12]
    hashed_key = hash_api_key(raw_key)
    return raw_key, prefix, hashed_key


def hash_api_key(raw_key: str) -> str:
    """Computes SHA-256 hash of a raw API key."""
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
