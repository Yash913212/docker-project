import base64
import time
import hmac
import hashlib
import struct

def generate_totp(secret, time_step=30, digits=6):
    # Convert Base32 or raw bytes
    if isinstance(secret, str):
        secret = secret.encode()

    # Current Unix time / 30 seconds
    counter = int(time.time()) // time_step

    # Convert counter to 8-byte array
    msg = struct.pack(">Q", counter)

    # HMAC-SHA1 (standard TOTP)
    hmac_digest = hmac.new(secret, msg, hashlib.sha1).digest()

    # Dynamic truncation
    offset = hmac_digest[-1] & 0x0F
    code = (struct.unpack(">I", hmac_digest[offset:offset+4])[0] & 0x7fffffff) % (10 ** digits)

    return str(code).zfill(digits)


def read_seed():
    with open("seed.txt", "rb") as f:
        seed = f.read().strip()
    return seed


if __name__ == "__main__":
    secret = read_seed()
    print("Current TOTP:", generate_totp(secret))
