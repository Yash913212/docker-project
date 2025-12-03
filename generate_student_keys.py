from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_rsa_keypair(key_size: int = 4096):
    """
    Generate RSA key pair
    
    Returns:
        Tuple of (private_key, public_key)
    """

    # Generate RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,   # required by assignment
        key_size=key_size
    )

    # Extract public key
    public_key = private_key.public_key()

    return private_key, public_key


def save_keys(private_key, public_key):
    """Save private and public keys to PEM files."""

    # Save private key
    with open("student_private.pem", "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,  # PKCS#1
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # Save public key
    with open("student_public.pem", "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    print("✔ student_private.pem and student_public.pem generated successfully")


if __name__ == "__main__":
    priv, pub = generate_rsa_keypair()
    save_keys(priv, pub)
