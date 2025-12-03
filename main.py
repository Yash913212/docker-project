from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64, os, time, hmac, hashlib, struct

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization


app = FastAPI()

SEED_PATH = "data/seed.txt"


# ========= MODELS =========
class DecryptRequest(BaseModel):
    encrypted_seed: str


class VerifyRequest(BaseModel):
    code: str


# ========= HELPERS =========

def load_private_key():
    with open("student_private.pem", "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def decrypt_seed_rsa(encrypted_seed_b64: str) -> str:
    private_key = load_private_key()
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)

    decrypted = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        )
    )

    seed_hex = decrypted.decode().strip()

    if len(seed_hex) != 64:
        raise ValueError("Invalid seed length")

    int(seed_hex, 16)
    return seed_hex


def generate_totp(secret_hex: str):
    secret = bytes.fromhex(secret_hex)
    timestep = 30
    counter = int(time.time()) // timestep

    msg = struct.pack(">Q", counter)
    hmac_digest = hmac.new(secret, msg, hashlib.sha1).digest()

    offset = hmac_digest[-1] & 0x0F
    code = (struct.unpack(">I", hmac_digest[offset:offset+4])[0] & 0x7fffffff) % 1_000_000

    return str(code).zfill(6)


def verify_totp(secret_hex: str, user_code: str):
    secret = bytes.fromhex(secret_hex)
    timestep = 30
    current_counter = int(time.time()) // timestep

    for offset in [-1, 0, 1]:
        counter = current_counter + offset
        msg = struct.pack(">Q", counter)

        hmac_digest = hmac.new(secret, msg, hashlib.sha1).digest()
        off = hmac_digest[-1] & 0x0F
        code = (struct.unpack(">I", hmac_digest[off:off+4])[0] & 0x7fffffff) % 1_000_000

        if str(code).zfill(6) == user_code:
            return True

    return False


@app.post("/decrypt-seed")
def decrypt_seed(body: DecryptRequest):
    try:
        seed_hex = decrypt_seed_rsa(body.encrypted_seed)

        os.makedirs("data", exist_ok=True)
        with open(SEED_PATH, "w") as f:
            f.write(seed_hex)

        return {"status": "ok"}

    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")


@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(SEED_PATH, "r") as f:
        seed_hex = f.read().strip()

    code = generate_totp(seed_hex)
    valid_for = 30 - (int(time.time()) % 30)

    return {"code": code, "valid_for": valid_for}


@app.post("/verify-2fa")
def verify_2fa(body: VerifyRequest):
    if body.code is None:
        raise HTTPException(status_code=400, detail="Missing code")

    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(SEED_PATH, "r") as f:
        seed_hex = f.read().strip()

    valid = verify_totp(seed_hex, body.code)
    return {"valid": valid}
