import os
import base64
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_message(words: list[str], message:str) -> dict:
    # Join words to form the "password"
    password = " ".join(words).encode()

    # Generate a random salt and derive a 256-bit key
    salt = os.urandom(16)
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    key = kdf.derive(password)

    # Encrypt using AES-GCM
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)

    # Encrypt the message
    ciphertext = aesgcm.encrypt(nonce, message.encode(), None)

    return {
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "salt": base64.b64encode(salt).decode()
    }

def decrypt_message(password: list[str], ciphertext: str, nonce: str, salt: str) -> str:
    # Join words to form the "password"
    password = " ".join(password).encode()

    # Decode the base64 encoded values
    ciphertext = base64.b64decode(ciphertext)
    nonce = base64.b64decode(nonce)
    salt = base64.b64decode(salt)

    # Derive the key using the same parameters
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    key = kdf.derive(password)

    # Decrypt using AES-GCM
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)

    return plaintext.decode()