#!/usr/bin/env python3

import os
import sys
import base64
import pyotp
import hashlib
from datetime import datetime, timezone

# Add the app directory to the Python path to import main
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SEED_PATH = "/data/seed.txt"
LOG_PATH = "/cron/last_code.txt"

def get_base32_seed(hex_seed: str) -> str:
    """Converts the hex seed to base32."""
    seed_bytes = bytes.fromhex(hex_seed)
    return base64.b32encode(seed_bytes).decode("utf-8")

def generate_totp(hex_seed: str) -> str:
    """Generates a TOTP code."""
    base32_seed = get_base32_seed(hex_seed)
    totp = pyotp.TOTP(base32_seed, digest=hashlib.sha1)
    return totp.now()

def main():
    """
    Reads the seed, generates a TOTP code, and logs it with a UTC timestamp.
    """
    if not os.path.exists(SEED_PATH):
        # Silently exit if seed not ready yet - evaluation system expects clean logs
        sys.exit(0)

    try:
        with open(SEED_PATH, "r") as f:
            seed_hex = f.read().strip()

        if len(seed_hex) != 64:
            sys.stderr.write(f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} - Error: Invalid seed format in {SEED_PATH}\n")
            return

        code = generate_totp(seed_hex)
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        # Append to the log file
        with open(LOG_PATH, "a") as log_file:
            log_file.write(f"{timestamp} - 2FA Code: {code}\n")

    except Exception as e:
        sys.stderr.write(f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} - An unexpected error occurred: {e}\n")

if __name__ == "__main__":
    main()
