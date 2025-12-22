from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import os
import time
import pyotp
import hashlib

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization

app = FastAPI()

# Use absolute path for Docker volume
SEED_PATH = "/data/seed.txt"


# ========= MODELS =========
class DecryptRequest(BaseModel):
    encrypted_seed: str


class VerifyRequest(BaseModel):
    code: str


# ========= HELPERS =========

def load_private_key():
    """Loads the student's private key from a PEM file."""
    with open("student_private.pem", "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def decrypt_seed_rsa(encrypted_seed_b64: str) -> str:
    """Decrypts the RSA/OAEP encrypted seed."""
    private_key = load_private_key()
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)

    decrypted = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    seed_hex = decrypted.decode().strip()

    # Validate that the decrypted seed is a 64-character hex string
    if len(seed_hex) != 64:
        raise ValueError(f"Invalid seed length: {len(seed_hex)}")
    int(seed_hex, 16)  # Will raise ValueError if not a valid hex

    return seed_hex


def get_base32_seed(hex_seed: str) -> str:
    """Converts the hex seed to base32 as required by TOTP standards."""
    seed_bytes = bytes.fromhex(hex_seed)
    return base64.b32encode(seed_bytes).decode("utf-8")


def generate_totp(hex_seed: str) -> str:
    """Generates a TOTP code using pyotp."""
    base32_seed = get_base32_seed(hex_seed)
    totp = pyotp.TOTP(base32_seed, digest=hashlib.sha1)
    return totp.now()


def verify_totp(hex_seed: str, user_code: str) -> bool:
    """Verifies a TOTP code with a +/- 1 period tolerance."""
    base32_seed = get_base32_seed(hex_seed)
    totp = pyotp.TOTP(base32_seed, digest=hashlib.sha1)
    return totp.verify(user_code, valid_window=1)


# ========= API ENDPOINTS =========

@app.get("/")
def root():
    """Lightweight health check endpoint for external monitors."""
    return {"status": "ok"}

@app.get("/healthz")
def healthz():
    """Kubernetes-style health endpoint."""
    return {"status": "ok"}

@app.post("/decrypt-seed")
def decrypt_seed(body: DecryptRequest):
    """
    Decrypts the seed, validates it, and stores it persistently.
    """
    try:
        seed_hex = decrypt_seed_rsa(body.encrypted_seed)

        # Ensure the /data directory exists
        os.makedirs(os.path.dirname(SEED_PATH), exist_ok=True)
        with open(SEED_PATH, "w") as f:
            f.write(seed_hex)

        return {"status": "ok"}

    except Exception as e:
        # Log the error for debugging; in production, use a proper logger
        print(f"Decryption failed: {e}")
        raise HTTPException(status_code=500, detail="Decryption failed")


@app.get("/generate-2fa")
def generate_2fa():
    """
    Generates a 2FA code from the stored seed.
    """
    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(SEED_PATH, "r") as f:
        seed_hex = f.read().strip()

    code = generate_totp(seed_hex)
    valid_for = 30 - (int(time.time()) % 30)

    return {"code": code, "valid_for": valid_for}


@app.post("/verify-2fa")
def verify_2fa(body: VerifyRequest):
    """
    Verifies a 2FA code provided by the user.
    """
    if not body.code:
        raise HTTPException(status_code=400, detail="Missing code")

    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(SEED_PATH, "r") as f:
        seed_hex = f.read().strip()

    is_valid = verify_totp(seed_hex, body.code)
    return {"valid": is_valid}
