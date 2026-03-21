from src.crypto_utils import generate_salt, derive_key, encrypt_password, decrypt_password
from src.storage import load_vault, save_vault

# Test master password
master_password = "MyMasterPassword"

# Generate salt
salt = generate_salt()

# Derive encryption key
key = derive_key(master_password, salt)

# Password we want to protect
password = "MySecretPassword123"

# Encrypt the password
nonce, ciphertext = encrypt_password(password, key)

print("Encrypted password:", ciphertext)

# Decrypt the password
decrypted = decrypt_password(ciphertext, nonce, key)

print("Decrypted password:", decrypted)

# Check if everything worked
if decrypted == password:
    print("Test successful: encryption and decryption work correctly")
else:
    print("Test failed")


# Test storage

vault = load_vault()
print("Loaded vault:", vault)

# Add dummy data
vault["entries"].append({
    "service": "Test",
    "username": "test_user",
    "nonce": "test_nonce",
    "ciphertext": "test_cipher"
})

save_vault(vault)

print("Vault updated and saved.")