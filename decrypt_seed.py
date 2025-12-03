import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization

def decrypt_seed():
    # Step 1: Load student private key
    with open("student_private.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )

    # Step 2: Read encrypted seed
    with open("encrypted_seed.txt", "r") as f:
        encrypted_b64 = f.read().strip()

    # Step 3: Base64 decode
    encrypted_bytes = base64.b64decode(encrypted_b64)

    # Step 4: Decrypt using RSA OAEP SHA-256
    decrypted_seed = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Step 5: Save final seed
    with open("seed.txt", "wb") as f:
        f.write(decrypted_seed)

    print("Seed decrypted and saved to seed.txt")


if __name__ == "__main__":
    decrypt_seed()
