from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

KEY_DIR = Path("./keys")
KEY_DIR.mkdir(parents=True, exist_ok=True)

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,  # like "genrsa"
    encryption_algorithm=serialization.NoEncryption(),
)

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,  # like "-pubout"
)

(KEY_DIR / "private.pem").write_bytes(private_pem)
(KEY_DIR / "public.pem").write_bytes(public_pem)

print("Generated:")
print(f" - {KEY_DIR / 'private.pem'}")
print(f" - {KEY_DIR / 'public.pem'}")