#!/usr/bin/env python3
"""
generate_commit_proof.py

Generates a signed+encrypted proof of the most recent git commit.

Outputs:
- Commit Hash (40 hex chars)
- Encrypted Signature (base64 single line)

Usage:
    py -3 generate_commit_proof.py
    # or
    python3 generate_commit_proof.py
"""

import subprocess
import base64
import sys
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric import utils as asym_utils
from cryptography.hazmat.backends import default_backend

STUDENT_PRIV_PATH = "student_private.pem"
INSTRUCTOR_PUB_PATH = "instructor_public.pem"


def get_latest_commit_hash() -> str:
    """Return latest commit hash (40-char hex) from git."""
    try:
        out = subprocess.check_output(["git", "log", "-1", "--format=%H"], stderr=subprocess.STDOUT)
        commit_hash = out.decode().strip()
        if len(commit_hash) != 40:
            raise ValueError(f"Unexpected commit hash length: '{commit_hash}'")
        return commit_hash
    except subprocess.CalledProcessError as e:
        print("Error running git. Make sure this repo has at least one commit.", file=sys.stderr)
        print(e.output.decode(), file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("git not found. Please install git or run this script from a git repo.", file=sys.stderr)
        sys.exit(1)


def load_private_key(path: str):
    """Load an unencrypted PEM RSA private key from file."""
    with open(path, "rb") as f:
        keydata = f.read()
    try:
        private_key = serialization.load_pem_private_key(keydata, password=None, backend=default_backend())
        return private_key
    except Exception as e:
        print(f"Failed to load private key {path}: {e}", file=sys.stderr)
        sys.exit(1)


def load_public_key(path: str):
    """Load a PEM public key (SubjectPublicKeyInfo) from file."""
    with open(path, "rb") as f:
        keydata = f.read()
    try:
        public_key = serialization.load_pem_public_key(keydata, backend=default_backend())
        return public_key
    except Exception as e:
        print(f"Failed to load public key {path}: {e}", file=sys.stderr)
        sys.exit(1)


def sign_message(message: str, private_key) -> bytes:
    """
    Sign a message (ASCII string) using RSA-PSS with SHA-256.

    - message: ASCII string (commit hash)
    - private_key: RSA private key object from cryptography
    Returns signature bytes.
    """
    message_bytes = message.encode("utf-8")  # ASCII/UTF-8 bytes of commit hash
    signature = private_key.sign(
        message_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature


def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    """
    Encrypt data using RSA/OAEP with SHA-256 (MGF1 SHA-256).
    Returns ciphertext bytes.
    """
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext


def main():
    # 1. Get commit hash
    commit_hash = get_latest_commit_hash()
    print("Commit Hash:", commit_hash)

    # 2. Load student private key
    priv = load_private_key(STUDENT_PRIV_PATH)

    # 3. Sign commit hash (ASCII)
    sig = sign_message(commit_hash, priv)

    # 4. Load instructor public key
    pub = load_public_key(INSTRUCTOR_PUB_PATH)

    # 5. Encrypt signature with instructor public key (OAEP SHA-256)
    encrypted_sig = encrypt_with_public_key(sig, pub)

    # 6. Base64 encode
    encrypted_b64 = base64.b64encode(encrypted_sig).decode("ascii")

    print("\nEncrypted Signature (base64):")
    print(encrypted_b64)
    print("\n---")
    print("Copy the Encrypted Signature (single line) above to submit with your repo.")


if __name__ == "__main__":
    main()
