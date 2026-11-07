"""Solana Ed25519 Wallet and Keypair Management."""

from __future__ import annotations

import base58
import hashlib
from typing import Optional, Tuple
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


class SolanaWallet:
    """Manages an Ed25519 Solana wallet keypair with base58 encoding and signature capabilities."""

    def __init__(self, private_key: Optional[ed25519.Ed25519PrivateKey] = None):
        if private_key is None:
            self._private_key = ed25519.Ed25519PrivateKey.generate()
        else:
            self._private_key = private_key
        self._public_key = self._private_key.public_key()

    @classmethod
    def generate(cls) -> SolanaWallet:
        """Generate a fresh random Solana wallet."""
        return cls()

    @classmethod
    def from_seed(cls, seed: bytes) -> SolanaWallet:
        """Create a deterministic wallet from a 32-byte seed."""
        if len(seed) != 32:
            seed = hashlib.sha256(seed).digest()
        priv = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
        return cls(priv)

    @classmethod
    def from_seed_phrase(cls, phrase: str) -> SolanaWallet:
        """Create a deterministic wallet from a seed string or passphrase."""
        seed = hashlib.sha256(phrase.encode("utf-8")).digest()
        return cls.from_seed(seed)

    @classmethod
    def from_base58_secret(cls, secret_b58: str) -> SolanaWallet:
        """Instantiate wallet from a base58 encoded private key (or 64-byte secret key)."""
        raw = base58.b58decode(secret_b58)
        # Solana keypairs are usually 64 bytes (32 bytes seed/priv + 32 bytes pub)
        seed = raw[:32]
        priv = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
        return cls(priv)

    @property
    def public_key_bytes(self) -> bytes:
        """Raw 32-byte public key."""
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

    @property
    def public_key(self) -> str:
        """Base58-encoded public address on Solana."""
        return base58.b58encode(self.public_key_bytes).decode("ascii")

    @property
    def secret_key_bytes(self) -> bytes:
        """Standard 64-byte secret key (32-byte private key + 32-byte public key)."""
        priv_bytes = self._private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        return priv_bytes + self.public_key_bytes

    @property
    def secret_key(self) -> str:
        """Base58-encoded secret key."""
        return base58.b58encode(self.secret_key_bytes).decode("ascii")

    @property
    def secret_key_base58(self) -> str:
        """Alias for secret_key base58 representation."""
        return self.secret_key

    def sign(self, message: bytes) -> bytes:
        """Sign a message using Ed25519."""
        return self._private_key.sign(message)

    def sign_base58(self, message: bytes) -> str:
        """Sign a message and return the base58 encoded signature."""
        sig = self.sign(message)
        return base58.b58encode(sig).decode("ascii")

    def verify(self, message: bytes, signature: bytes) -> bool:
        """Verify an Ed25519 signature against this wallet's public key."""
        try:
            self._public_key.verify(signature, message)
            return True
        except Exception:
            return False

    @staticmethod
    def verify_signature(public_key_b58: str, message: bytes, signature_b58: str) -> bool:
        """Verify any base58 signature against any base58 public key."""
        try:
            pub_bytes = base58.b58decode(public_key_b58)
            sig_bytes = base58.b58decode(signature_b58)
            pub = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
            pub.verify(sig_bytes, message)
            return True
        except Exception:
            return False

    def __repr__(self) -> str:
        return f"<SolanaWallet pubkey={self.public_key[:8]}...{self.public_key[-4:]}>"
