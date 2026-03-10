import os #generate secure random values

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# crypto_utils.py

# This file contains all cryptographic operations used in the password manager.
# It handles key generation, encryption and decryption.

def generate_salt():
    # Create a random salt value used when generating the encryption key 
    return os.urandom(16) # generates cryptographically secure random bytes (16 = 128 bits)


def derive_key(master_password, salt):
    # Turn the master password into a secure encryption key
    kdf = PBKDF2HMAC( # function that turns the master password into a key 
        algorithm=hashes.SHA256(), # hashing algorithm
        length=32, # 32-byte key (suitable for AES-256)
        salt=salt,
        iterations=100000, # repeats the process X times
    )
    return kdf.derive(master_password.encode())


def encrypt_password(password, key):
    # Encrypt the password before saving it to the vault
    aesgcm = AESGCM(key) # creates an AES-GCM object using the key generated from the master password
    nonce = os.urandom(12) # 12 bytes (standard size fro AES-GCM)
    ciphertext = aesgcm.encrypt(nonce, password.encode(), None) # performs the encryption
    return nonce, ciphertext



def decrypt_password(ciphertext, nonce, key):
    # Decrypt the stored password when the user wants to view it
    aesgcm = AESGCM(key) 
    plaintext = aesgcm.decrypt(nonce, ciphertext, None) # decrypts process
    return plaintext.decode() # coverts bytes back into normal text