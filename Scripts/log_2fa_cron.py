#!/usr/bin/env python3

import time
import hmac
import hashlib
import struct
from datetime import datetime, timezone
import os


SEED_PATH = "/data/seed.txt"


def generate_totp(secret_hex: str, time_step=30, digits=6):
    secret = bytes.fromhex(secret_hex)
    counter = int(time.time()) // time_step

    msg = struct.pack(">Q", counter)
    hmac_digest = hmac.new(secret, msg, hashlib.sha1).digest()

    offset = hmac_digest[-1] & 0x0F
    code = (struct.unpack(">I", hmac_digest[offset:offset+4])[0] & 0x7fffffff) % (10 ** digits)

    return str(code).zfill(digits)


def main():
    # 1. Read seed
    if not os.path.exists(SEED_PATH):
        print("Seed not found, cron cannot generate 2FA code.")
        return

    with open(SEED_PATH, "r") as f:
        seed_hex = f.read().strip()

    # 2. Generate TOTP
    code = generate_totp(seed_hex)

    # 3. Current UTC time
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # 4. Log
    print(f"{timestamp} - 2FA Code: {code}")


if __name__ == "__main__":
    main()
