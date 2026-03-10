# crypto_utils.py


# This file contains all cryptographic operations used in the password manager.
# It handles key generation, encryption and decryption.

def generate_salt():
    # Create a random salt value used when generating the encryption key 
    pass


def derive_key(master_password, salt):
    # Turn the master password into a secure encription key
    pass


def encrypt_password(password, key):
    # Encrypt the password before saving it to the vault
    pass


def decrypt_password(ciphertext, nonce, key):
    # Decrypt the stored password then the user wants to view it
    pass