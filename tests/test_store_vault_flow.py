from src.storage import load_vault, save_vault
from src.crypto_utils import (
    generate_salt,
    derive_key,
    encrypt_password,
    bytes_to_base64,
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
from src.crypto_utils import base64_to_bytes
salt = base64_to_bytes(vault["salt"])

# Derive key from master password + salt
key = derive_key(master_password, salt)

# Test entry
service = "Gmail"
username = "lucas@gmail.com"
password = "MySecretPassword123"

# Encrypt password
nonce, ciphertext = encrypt_password(password, key)

# Save encrypted entry in Base64 format
entry = {
    "service": service,
    "username": username,
    "nonce": bytes_to_base64(nonce),
    "ciphertext": bytes_to_base64(ciphertext),
}

vault["entries"].append(entry)
save_vault(vault)

print("Encrypted entry saved successfully.")