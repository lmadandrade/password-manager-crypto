from src.storage import load_vault, save_vault
from src.crypto_utils import (
    generate_salt,
    derive_key,
    encrypt_password,
    decrypt_password,
    bytes_to_base64,
    base64_to_bytes,
)

# Test master password
master_password = "MyMasterPassword"

# Load vault
vault = load_vault()

# Create salt if it does not exist yet
if vault["salt"] is None:
    salt = generate_salt()
    vault["salt"] = bytes_to_base64(salt)
    save_vault(vault)
    print("New salt generated and saved.")
else:
    print("Salt already exists in vault.")

# Convert stored Base64 salt back to bytes
salt = base64_to_bytes(vault["salt"])

# Derive key from master password + salt
key = derive_key(master_password, salt)

# Only add a test entry if the vault is empty
if not vault["entries"]:
    service = "Gmail"
    username = "lucas@gmail.com"
    password = "MySecretPassword123"

    nonce, ciphertext = encrypt_password(password, key)

    entry = {
        "service": service,
        "username": username,
        "nonce": bytes_to_base64(nonce),
        "ciphertext": bytes_to_base64(ciphertext),
    }

    vault["entries"].append(entry)
    save_vault(vault)
    print("Encrypted entry saved successfully.")

# Load the first saved entry
entry = vault["entries"][0]

# Convert Base64 values back to bytes
stored_nonce = base64_to_bytes(entry["nonce"])
stored_ciphertext = base64_to_bytes(entry["ciphertext"])

# Decrypt the saved password
decrypted_password = decrypt_password(stored_ciphertext, stored_nonce, key)

print("Decrypted entry details:")
print("Service:", entry["service"])
print("Username:", entry["username"])
print("Password:", decrypted_password)